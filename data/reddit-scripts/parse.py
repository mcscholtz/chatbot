import os
import json
import re
import pickle
import unicodedata
from sets import Set
from functools import partial
import time

import multiprocessing
from multiprocessing import Process, Queue, Pool

#sub_reddit_blacklist = Set(['de', 'Romania', 'hola', 'croatia', 'sweden'])
sub_reddit_blacklist = []
class Comment:
    def __init__(self, jsonObject):
        self.id = jsonObject['id']       
        self.link_id = re.sub(b'^t[1-5]_', '', jsonObject['link_id'])
        self.parent_id = re.sub(b'^t[1-5]_', '', jsonObject['parent_id'])
        self.body = jsonObject['body']
        self.subreddit = jsonObject['subreddit']    

def parseWorker(f, data):   
    comments = []   
    regEx_keep = [  re.compile(b'\\n'), 
                    re.compile(b'&amp;'), 
                    re.compile(b'nbsp;'), 
                    re.compile(b'&gt;'), 
                    re.compile(b'&lt;'), 
                    re.compile(b'\[.*?\]'), 
                    re.compile(b'\(.*?\)'), 
                    re.compile(b'"'), 
                    re.compile(b'[^\x00-\x7F]'),
                    re.compile(b'\s{2}')
                ]
    sub_string = [' ', '&', ' ', '', '', '', '', '', '', '']
    regEx_emoji = [ re.compile(b':3'), 
                    re.compile(b':-3'), 
                    re.compile(b'8-\)'), 
                    re.compile(b'8\)'), 
                    re.compile(b':o\)'), 
                    re.compile(b':c\)'), 
                    re.compile(b'8\-D'),
                    re.compile(b'8D'), 
                    re.compile(b'=3'), 
                    re.compile(b':\-O'), 
                    re.compile(b':\-o'), 
                    re.compile(b':o'),
                    re.compile(b':0'), 
                    re.compile(b'8-0'), 
                    re.compile(b'>:O'), 
                    re.compile(b'O:-\)'), 
                    re.compile(b'0:-3'), 
                    re.compile(b'0:-\)'), 
                    re.compile(b'0;\^\)'), 
                    re.compile(b'O:\)'), 
                    re.compile(b'0:3'), 
                    re.compile(b'0:\)'), 
                    re.compile(b'3:-\)'), 
                    re.compile(b'3:\)'), 
                    re.compile(b'\|-O'), 
                    re.compile(b'<3'), 
                    re.compile(b'<\\\\3'), 
                    re.compile(b'\\o\/'), 
                    re.compile(b'\*\\0\/\*')
                ]
    
    regEx_disc = [  re.compile(b'(.)\1{2,}'),
                    re.compile(b'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'), 
                    #re.compile(b'\*'), 
                    #re.compile(b'[<>,=:+~`\'"#%\^\|\-\/\*@;)(]'), 
                    #re.compile(b'\.{2,}'), 
                    #re.compile(b'\s[qwertyupsdfghjklzxcvbnmQWERTYUOPSDFGHJKLZXCVBNM]$'), 
                    #re.compile(b'\s[qwertyupsdfghjklzxcvbnmQWERTYUOPSDFGHJKLZXCVBNM]\s'), 
                    #re.compile(b'\s[0-9]$')
                ]    
    regEx_word = [re.compile(b'[.\?,"]')]     
   
    for line in data:          
        j = json.loads(line)                        
        if j['subreddit'] not in sub_reddit_blacklist:                     
            
            #Substitution regex's            
            msg = j['body']
            #for r in range(0, len(regEx_emoji)): 
            #    msg = regEx_emoji[r].sub('', msg)
            for r in range(0, len(regEx_keep)): 
                msg = regEx_keep[r].sub(sub_string[r], msg)
                
            #if any discard regex's match, ignore the comment and go to the next one             
            skip = False                
            for r in range(0, len(regEx_disc)):            
                if regEx_disc[r].search(msg):
                    skip = True            
            if skip == True:
                continue
                           
            msg = msg.lower()
            msg = msg.strip()
            words = msg.split(' ')
            wordCount = len(words)
            if wordCount > 50:
                continue                           
            if msg != '[deleted]' and msg != '[removed]' and msg != '':                                                            
                comment = {}                    
                comment['id'] = j['id']
                comment['link_id'] = j['link_id']
                comment['parent_id'] = j['parent_id']
                comment['subreddit'] = j['subreddit']
                comment['body'] = msg
                comment['score'] = j['score']
                comments.append(comment)
    #print 'closing worker thread'
    thread = multiprocessing.current_process()
    num = thread.name.split('-')
    #exit()    
    filename =  'data-' + str(f) + '-' + num[1]
    f += 1                            
    save_obj(os.path.join('parsed', filename), comments)

#filesize is the number of comments that will be saved per file. if this is too high the system will run out of memory
#queue_size is how large the queue buffer is for each thread. Again if this is too high the system will run out of memory
def parse(dump_file, chunk_size, num_workers, f):
    print dump_file   
    blocks = chunk_size*num_workers    
    i = 0
    p = Pool(num_workers)
    chunks = []
    name = []
    for x in xrange(0, num_workers):
        chunks.append([])
        name.append(x)
  
    with open(dump_file, 'rb') as dump:
        for line in dump:        
                        
            k = i % num_workers           

            chunks[k].append(line)
            i += 1
            #when the lists are ready to be processed            
            if i % blocks == 0:
                #start pool
                func = partial(parseWorker, f)             
                start = p.map(func, chunks)
                #clear chucks
                chunks = []
                i = 0
                for x in xrange(0, num_workers):
                    chunks.append([])     
                f += 1
        #Handle remaining data in lists
        func = partial(parseWorker, f)
        start = p.map(func, chunks)
        print f 
        p.close()        
        p.join()
    return f

def save_obj(filename, data):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
        #print("Saved ", filename, " file")


def get_all(directory, f):     
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            f = parse(os.path.join(directory, file), 31250, 3, f)

get_all('/media/jump-drive/reddit', 0)

#parse(os.path.join('/media/jump-drive/reddit', 'RC_2011-08'), 31250, 8, 555)

