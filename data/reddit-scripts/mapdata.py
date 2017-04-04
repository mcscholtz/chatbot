import os, pickle
import json, re
import multiprocessing
from multiprocessing import Process, Queue, Pool
from functools import partial
import time

#primary loop
def assemble(directory, num_workers, batch_number):
    filePaths = []  
    for subdir, dirs, files in os.walk(directory):   
        for file in files:        
            path = os.path.join(subdir, file)            
            filePaths.append(path)
    lists = group(filePaths, num_workers)
    p = Pool(num_workers)
    j = 0
    k = 0    
    for item in lists:
        batch = group(item, batch_number)
        if batch_number > num_workers:
                        
            #ratio = batch_number/num_workers            
            for b in batch:
                sub_batch = group(b, num_workers)
                mapped = p.map(mapWorker, sub_batch)
                print 'Merging worker maps...'       
                merged = mergeSubreddits(mapped)
                name = 'data-map' + str(j)
                with open(os.path.join('data-map', name), 'wb') as file:
                    pickle.dump(merged, file)
                print len(merged), 'subreddit maps saved as data-map'
                j+=1            
        else:
            batch = group(item, batch_number) 
            mapped = p.map(mapWorker, batch)
            print 'Merging worker maps...'       
            merged = mergeSubreddits(mapped)
            name = 'data-map' + str(j)
            with open(os.path.join('data-map', name), 'wb') as file:
                pickle.dump(merged, file)
            print len(merged), 'subreddit maps saved as data-map'
            j+=1
    p.close()
    p.join()                         

def mergeDataMaps(directory):
    for subdir, dirs, files in os.walk(directory):   
        lastDict = {}        
        for file in files:
            with open(os.path.join(subdir, file), 'rb') as dataMap:
                data = pickle.load(dataMap)
                if lastDict == {}:
                    lastDict = data
                else:
                    lastDict = mergeSubreddits([lastDict, data])
        with open('merged-data-map', 'wb') as file:
            pickle.dump(lastDict, file)
      
def mapSubreddits(filename):
    #goes through the file and map all the subreddits of the file into indexes (line numbers)
    subreddits = {}
    file = filename.split('/')
    print file
    #print subdir
    with open(filename, 'rb') as comments:
        data = pickle.load(comments)    
        j = 0    
        for line in data:             
            try:              
                #subreddit is already in the dict, retrief file dictionary                
                fdict = subreddits[line['subreddit']]
                #print fdict
                #exit()
                fdict[0]['indexes'].append(j)
                #print fdict
                #exit()
                subreddits[line['subreddit']] = fdict
                #print subreddits
            except KeyError:
                #means this subreddit is not in the dict yet, add it
                fdict = {}                
                fdict['file'] = file[1]
                fdict['indexes'] = [j]
                #print fdict
                subreddits[line['subreddit']] = [fdict]
               # print subreddits           
            j+=1
        #print subreddits
        #exit() 
    return subreddits        

def mergeSubreddits(mapp):
    #merge a list of dictionaries into 1 dectionary onject
    #MAX_DICT_SIZE = 5000
    print 'Merging maps..'
    merged = {}    #list to contain dictionaries 
    j = 0           
    for file in mapp:
        if merged == {}:
            merged = file
        else:            
            for key in file:  
                try:                    
                    fdict = merged[key]
                    #if j == 1: print file[key]
                    #if j == 1: print fdict
                    fdict.append(file[key][0])
                    #if j == 1: print fdict
                    #if j == 1: time.sleep(5)
                    merged[key] = fdict
                except KeyError:
                    #means this subreddit is not in the dict yet
                    merged[key] = file[key]
                    #for key in merged:               
                    #print key, merged[key]
                #exit()
        j+=1
    #for m in merged:
     #   print m
     #   print merged[m]
     #   time.sleep(5)                                   
    return merged    

def group(lst, div):
    lst = [ lst[i:i + len(lst)/div] for i in range(0, len(lst), len(lst)/div) ] #Subdivide list.
    if len(lst) > div: # If it is an uneven list.
        lst[div-1].extend(sum(lst[div:],[])) # Take the last part of the list and append it to the last equal division.
    return lst[:div] #Return the list up to that point.

def mapWorker(files): 
    mapp = []   
    for file in files:
        #if len(mapp) > 1:
        #    test = mergeSubreddits(mapp)    
        mapp.append(mapSubreddits(file))
    #now merge the mapped files
    return mergeSubreddits(mapp)

#Batch number must be a multiple of worker count
#its batch number per core, therefor 8 threads x 32 batches = 256 checkpoints will be saved before being merged
  
assemble('parsed', 4, 128)
mergeDataMaps('data-map')

