import zip as zip
import re, os
import unicodedata
import pickle
       
def count_lines(dir, regex):      
    count = 0
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            with open (os.path.join(subdir, file), 'rb') as file:
                for line in file:
                    if line == b'\r\n':
                        continue
                    if regex.match(line):
                        count +=1
    return count

def extract_dialog(dir, size, remove_line, remove, names):      
    line_number = 0
    dropped = 0
    parsed = 0
    convs = []
    conv = []
    cnt = 0
    for subdir, dirs, files in os.walk(dir):
        cnt = 0
        for file in files:
            with open(os.path.join(subdir, file), 'rb') as data:
                script = pickle.load(data)
                for line in script:
                    line_number +=1
                    line = line.lower()
                    line = line.replace(b"\r\n",b" ")
                    line = line.replace(b"\n",b" ")
                    line = line.replace(b"\r",b" ")
                    line = line.replace(b'\s{2}', b' ')
                    line = line.strip() 
                    #remove noise remove
                    skip = False
                    #print ("line: ", line)
                    #raw_input()
                    #test = re.compile(b'^[stardate:\s]')
                    #print remove_line
                    #print remove_line[1].match(line)
                    #print test.match(line)
                    #print re.match(b'^[stardate:\s]', line)
                    i=0
                    for regex in remove_line:
                        #print regex.match(line)
                        if regex.match(line):
                            #print i
                            #print "match!"
                            skip = True
                        i+=1
                    #raw_input()
                    if skip is True:
                        #print 'drop 1'
                        continue    
                    for regex in remove:
                        line = regex.sub(b'', line)
                    #Ignore blank lines
                    if line == b' ' or line == b'':
                        #print 'drop 2'
                        continue
                    if check_scene(line):
                        #print 'drop 3'
                        continue
                    #Remove unicode characters                    
                    try:                    
                        line = remove_accents(line)
                    except UnicodeDecodeError:
                        #print 'drop 4'
                        continue
                        #print line

                    m = names.match(line)
                    #Ignore lines that dont start with a speaker                    
                    try:
                        n = m.group(0)
                    except AttributeError:
                        #print 'drop 5'
                        continue
                    #print('Speaker:', n)
                    #print ('line passed:', line)
                    #print line
                    #exit()
                    
                    if conv == []:
                        conv.append(line)
                        cnt+=1
                    else:
                        status = eval_seq(conv, line)
                        if status is True:
                            conv.append(line)
                        else:
                            #Conv seq is over
                            if len(conv) >= size:
                                #Save conv because it met the min length, discard the last line if its odd                               
                                if len(conv) % 2 != 0:
                                    tmp = []                                    
                                    for i in range(0,(len(conv)-1)):
                                        tmp.append(conv[i])
                                    convs.append(tmp)
                                    #print tmp
                                    #print('\n'.join('{}: {}'.format(*k) for k in enumerate(tmp)))     
                                else:                                
                                    convs.append(conv)
                                    #print conv
                                    #print('\n'.join('{}: {}'.format(*k) for k in enumerate(conv)))  
                                conv = []
                            else:
                                while conv != []:
                                    conv = shift_list(conv)
                                    status = eval_seq(conv, line)
                                    if status is True:
                                        conv.append(line)
                                        break
    return convs                                 
                 
def shift_list(list):
    new_list = []
    n=0
    for item in list:
        if n!=0:
           new_list.append(item)
        n+=1
    return new_list     

def eval_seq(seq, line):
    speakerEven = ''
    speakerOdd = ''       
    cnt = 0    
    for s in seq:
        if speakerEven == '':
            speakerEven = get_speaker(s)
            cnt+=1
        elif speakerOdd == '':
            speakerOdd = get_speaker(s)
            cnt+=1
        else:
            if cnt % 2 == 0: 
                #sanity check                
                if get_speaker(s) !=  speakerEven:
                    print('ERR-EVEN')
                    exit()
            else:
                #sanity check                
                if get_speaker(s) !=  speakerOdd:
                    print('ERR-ODD')
                    exit()
            cnt+=1
    if speakerOdd != '':
        if cnt % 2 == 0:
            if get_speaker(line) ==  speakerEven:
                return True
            else:
                return False
        else:
            if get_speaker(line) ==  speakerOdd:        
                return True
            else:
                return False                       
    else:
        return True

def check_scene(line):
    if re.match(b'^(Scene:)', line):
        return True
    else:
        return False
        
def get_speaker(line):
    m = re.match(b'^(^[A-Za-z ]*/?)', line)
    return m.group(0)

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str.decode('unicode_escape'))
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

def strip_speakers(data, regex):
    conv = []
    convs = []
    for element in data:
        for line in element:
            conv.append(regex.sub(b'', line))
        convs.append(conv)
        #print('\n'.join('{}: {}'.format(*k) for k in enumerate(conv)))  
        #raw_input()
        #print('\n'.join('{}: {}'.format(*k) for k in enumerate(conv)))  
        conv = []
    return convs

def parse(dir):
    zip.unzip('chakoteya.zip', dir)    
    names = re.compile(b'^(.*?:\s)')
    remove_line = [re.compile(b'^original airdate:\s'), re.compile(b'^stardate:\s')]
    remove = [re.compile(b'\((.*?)\)\.'), re.compile(b'\s\((.*?)\)'), re.compile(b'\((.*?)\)')]

    #the 4 means, only sequences of 2 speakers alternating conversations for atleast 4 lines will be used
    convs = extract_dialog(dir,4, remove_line, remove, names)

    lines= 0
    for conv in convs:
        for line in conv:
            lines+=1

    print(len(convs), 'conversations containing', lines, 'lines')
    data = strip_speakers(convs, names)

    #Save list as a python object
    with open(os.path.join(dir,'chakoteya.conv'), 'wb') as fp:
        pickle.dump(data, fp)