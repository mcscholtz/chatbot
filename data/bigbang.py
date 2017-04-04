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

def extract_dialog(dir, size, remove, names):      
    line_number = 0
    dropped = 0
    parsed = 0
    convs = []
    conv = []
    cnt = 0
    for subdir, dirs, files in os.walk(dir):
        cnt = 0
        for file in files:
            #print(os.path.join(subdir, file))
            with open (os.path.join(subdir, file), 'rb') as script:
                for line in script:
                    line_number +=1
                    #remove noise remove
                    for regex in remove:
                        line = regex.sub(b'', line)
                    #Ignore blank lines
                    if line == b'\r\n' or line == b'' or line == b' \r\n':
                        continue
                    if check_scene(line):
                        continue
                    #Remove unicode characters                    
                    try:                    
                        line = remove_accents(line)
                    except UnicodeDecodeError:
                        continue
                        #print line
                    line = line.strip()
                    line = line.lower()
                    m = names.match(line)
                    #Ignore lines that dont start with a speaker                    
                    try:
                        n = m.group(0)
                    except AttributeError:
                        continue
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
                                else:                                
                                    convs.append(conv)
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
        conv = []
    return convs

def parse(dir):
    zip.unzip('bigbang.zip', dir)    
    names = re.compile(b'^(.*?:\s)')
    remove = [re.compile(b'\((.*?)\)\.'), re.compile(b'\s\((.*?)\)'), re.compile(b'\((.*?)\)')]

    #the 4 means, only sequences of 2 speakers alternating conversations for atleast 4 lines will be used
    convs = extract_dialog(dir,4, remove, names)

    lines= 0
    for conv in convs:
        for line in conv:
            lines+=1

    print(len(convs), 'conversations containing', lines, 'lines')
    data = strip_speakers(convs, names)

    #Save list as a python object
    with open(os.path.join(dir,'bigbang.conv'), 'wb') as fp:
        pickle.dump(data, fp)
