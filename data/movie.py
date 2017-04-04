
import random
import pickle
import sys, codecs, re, os
import zip as zip

''' 
    1. Read from 'movie-lines.txt'
    2. Create a dictionary with ( key = line_id, value = text )
'''
def get_id2line(dir):
    lines=open(os.path.join(dir,'movie_lines.txt')).read().split('\n')
    id2line = {}
    for line in lines:
        _line = line.split(' +++$+++ ')
        if len(_line) == 5:
            id2line[_line[0]] = _line[4]
    return id2line

'''
    1. Read from 'movie_conversations.txt'
    2. Create a list of [list of line_id's]
'''
def get_conversations(dir):
    conv_lines = open(os.path.join(dir,'movie_conversations.txt')).read().split('\n')
    convs = [ ]
    for line in conv_lines[:-1]:
        _line = line.split(' +++$+++ ')[-1][1:-1].replace("'","").replace(" ","")
        convs.append(_line.split(','))
    return convs
    
#This function groups all conversations in pairs.
#It also discards the last conversation where there are an odd number of exchanges
def reshape(convs):   
    mergedList = []
    tempList = []
    i=0
    j=0
    droppedLines = 0
    for conversation in convs:
        length = len(conversation)
        if(length % 2 != 0):
            length = length - 1
        for line in conversation:
            j = j+1
            if(j == length):
                tempList.append(line)
                mergedList.append(tempList)
                tempList = []
                i=0
                j=0
                droppedLines = droppedLines+1
                break
            elif(i < 2):
                tempList.append(line)
                i = i+1
            if(i == 2):
                mergedList.append(tempList)
                tempList = []
                i=0
    return(mergedList)

def replaceID(lines, dir):
    mergedConv = reshape(get_conversations(dir))
    convertedList = []
    tempList = []
    i = 0    
    for conv in mergedConv:
        s=False        
        for line in conv:            
            if lines[line] == '':
                #print('FOUND an empty line!!!!!')
                i+=1
                s=True       
        if s == False:        
            for line in conv:
                try:
                    tempList.append(stripGarbage(lines[line]))
                except UnicodeEncodeError:
                    print("NO SUCH ITEM IN DICTIONARY!!!")
            convertedList.append(tempList)
            tempList = []
    #print('Dropped ', i, 'conversations due to empty responses')
    return convertedList

def stripGarbage(line):
    line = re.sub(b'\s(-){2}', b'', line)
    line = re.sub(b'[^\x00-\x7F]+', b'', line)
    line = re.sub(b'(\.){3}\s', b'', line)
    line = re.sub(b'(\.){3}', b' ', line)
    line = line.lower()
    return line

def parse(dir):
    zip.unzip('movie.zip', dir)
    lines = get_id2line(os.path.join(dir,'data'))   
    convertedList = replaceID(lines, os.path.join(dir,'data'))
    lines= 0
    for conv in convertedList:
        for line in conv:
            lines+=1
    print(len(convertedList), 'conversations containing', lines, 'lines')

    with open(os.path.join(dir,'movie.conv'), 'wb') as fp:
        pickle.dump(convertedList, fp)
