import os, pickle
import json, re
import multiprocessing
from multiprocessing import Process, Queue, Pool, freeze_support
from functools import partial
import itertools
import time

class Worker(Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue= queue

    def run(self):
        print 'Worker started....', multiprocessing.current_process() 
        #print 'Computing things!'
        for data in iter( self.queue.get, None ):
            index = data[0]            
            subreddit = data[1]
            comments = []            
            for file in data[2]:
                with open(os.path.join('parsed', file['file']), 'rb') as f:
                    d = pickle.load(f)
                    for i in file['indexes']:
                        #do a sanity check to test code
                        if d[int(i)]['subreddit'] != subreddit:
                            print 'SUBREDDIT DOES NOT MATCH!!!'
                            print d[int(i)]['subreddit'], subreddit
                            exit() 
                        comments.append(d[int(i)])
            with open(os.path.join('by-subreddit', subreddit), 'wb') as file:
                pickle.dump(comments, file)
                print index, " Saved ", subreddit



def assemble_workers(directory, num_workers, start_at=0):  
    #Open data-map
    print 'Loading data-map...'
    with open('merged-data-map', 'rb') as d:
        dataMap = pickle.load(d)
        i = 0
        #total_time = 0        
        #average_time = 0
        _start = False
        p = Pool(num_workers)
        length = len(dataMap)
        request_queue = Queue(maxsize=32)
        for worker in xrange(num_workers):
            Worker(request_queue).start() 
        for x in xrange(0, length):         
            #Prepare batch data
            iterator = iter(dataMap)
            item = iterator.next()            
            if x < start_at:
                del dataMap[item]
                continue
            else:
                print ('Iteration: ', x)                        
                batch = [i, item, dataMap[item]]
                del dataMap[item]         
                request_queue.put(batch)
                print 'Put batch ', batch[0], batch[1]
            i +=1
        for j in xrange(num_workers):
            request_queue.put(None)


#freeze_support()  
#assemble('parsed', 4, 2, 'bitchimamoose')
assemble_workers('parsed', 6, 59250)

