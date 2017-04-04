import os, pickle
import json, re
import multiprocessing
import time
from treelib import Node, Tree
from multiprocessing import Process, Queue, Pool
from functools import partial
from sets import Set
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler 
import random

class Conv(object):
    def __init__(self, obj):
        regEx = re.compile(b'^t[1-5]_')        
        self.id = obj['id']
        self.parent_id = regEx.sub('', obj['parent_id'])
        self.link_id = regEx.sub('', obj['link_id'])
        self.subreddit = obj['subreddit']
        self.score = obj['score']
        self.body = obj['body']
    
class FileDetector(PatternMatchingEventHandler):
    patterns = ["*"]
    #def __init__(self):
    #    self.convs = []
    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        time.sleep(5)        
        # the file will be processed there
        print event.src_path, event.event_type  # print now only for degug
        with open(event.src_path, 'rb') as comments:
            data = pickle.load(comments)
            #for comment in data:
            commentList = {v['id']:v for v in data}.values()                      
            trees = findBranches(commentList)
            length = 0
            convs = []
            for tree in trees:
                tree = pruneBranches(tree, tree.root)
                conv = getConv(tree, tree.root, [])
                    #when the conv is an odd length, discard the last comment
                #print 'conv', conv
                if len(conv) > 0:                    
                    if len(conv) % 2 != 0:
                            #print conv
                        conv = discardLast(conv)
                        length += len(conv)
                    convs.append(conv)
                    name = event.src_path.split('/')[5]

            if len(convs) > 0:       
                with open(os.path.join('linked', name), 'wb') as f:
                    pickle.dump(convs, f)
                    print len(convs), 'comments saved.'   
                    convs = []
        os.remove(event.src_path)    

    def on_created(self, event):
        self.process(event)

def start():
        
    observer = Observer()
    print 'Watching for files created in /media/jump-drive2/reddit/by-subreddit....'
    observer.schedule(FileDetector(), path='/media/jump-drive2/reddit/by-subreddit')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
           
#primary loop
def assemble(directory, file_size):
    prunedTrees = []  
    for subdir, dirs, files in os.walk(directory):   
        convs = []        
        t0 = time.time()         
        for file in files:
            print 'Opening...', os.path.join(subdir, file)           
            with open(os.path.join(subdir, file), 'rb') as comments:
                data = pickle.load(comments)
                #for comment in data:
                #Remove duplicates
                commentList = {v['id']:v for v in data}.values()

                    #Get all trees                    
                #t0 = time.time()                       
                trees = findBranches(commentList)
                #t1 = time.time()
                #convs = []
                length = 0
                for tree in trees:
                    tree = pruneBranches(tree, tree.root)
                    conv = getConv(tree, tree.root, [])
                    #when the conv is an odd length, discard the last comment                    
                    if len(conv) % 2 != 0:
                        #print conv
                        conv = discardLast(conv)
                    length += len(conv)
                    convs.append(conv)
                    if len(convs) == file_size:
                        with open(os.path.join('linked', file), 'wb') as f:
                            pickle.dump(convs, f)
                            print len(convs), 'comments saved under', file    
                            print 'Contained...', length, 'conversations'
                            convs = []
        print len(convs)
        t1 = time.time()
        print t1-t0
        exit()
        if convs != []:                
            with open(os.path.join('convs', file), 'wb') as f:
                pickle.dump(convs, f)
                print len(convs), 'comments saved under', file

def discardLast(comments):
    length = len(comments)-1
    res = []
    for x in xrange(0, length):
        res.append(comments[x])
    return res    

def getConv(tree, node, comments):
    n = tree.get_node(node)
    comments.append(n.data.body)
    for child in tree.children(node):
        comments = getConv(tree, child.data.id, comments)   
    return comments         
          
def pruneBranches(tree, root):
    #tree.show(data_property="id")    
    depth = []
    #print root.data.body 
    for leaf in tree.children(root):
        #print 'i-1', leaf.data.body
        #print tree.get_node(leaf)
        depth.append({'depth':tree.depth(leaf), 'leaf':leaf})
    best = {}
    for branch in depth:
        if best == {}:
            best = branch
        elif branch['depth'] > best['depth']:
            #replace best and remove old best
            tree.remove_node(best['leaf'].data.id)
            best = branch
        elif branch['depth'] < best['depth']:
            tree.remove_node(branch['leaf'].data.id)
        else:          
            if branch['leaf'].data.score > best['leaf'].data.score:
                tree.remove_node(best['leaf'].data.id)
                best = branch
            elif branch['leaf'].data.score < best['leaf'].data.score:
                tree.remove_node(branch['leaf'].data.id)
            else:
                #branch and score are equal, select at random
                toss = random.randint(1, 2)
                if toss == 1:
                    tree.remove_node(best['leaf'].data.id)
                    best = branch
                else:
                    tree.remove_node(branch['leaf'].data.id)             
    #step through each child and repeat recursivly    
    for leaf in tree.children(root):
        #print 'i-2', leaf.data.id
        #print leaf.data.body
        #if tree.leaves(leaf) != []: 
        tree = pruneBranches(tree, leaf.data.id)
    return tree                   

def findBranches(comments): 
    trees = []
    commentMap = []
    noChild = []
    i = 0
    regEx_id = re.compile(b'^t[1-5]_')
    
    for comment in comments:             
        tree = findChildNodes(comment, comments, Tree())

        if tree.depth() == 0:
            #Dont add empty trees
            pass
        else:
            #Add tree to list
            #if tree.depth() > 1:
            #    tree.show(data_property="id")
                #raw_input()
            #tree.show(data_property="id")
            trees.append(tree)
    return trees

#TODO: The child nodes in the recursive part are not being added properly, they are found but the tree remains empty
def findChildNodes(root, comments, tree):  

    if tree.contains(root['id']):
        pass
    else:
        tree.create_node(root['id'], root['id'], data=Conv(root))
        
    regEx_id = re.compile(b'^t[1-5]_')
    for comment in comments:
        if root['id'] == regEx_id.sub('', comment['parent_id']):
            #found a match, now recurse to find children of the child        
            tree.create_node(comment['id'], comment['id'], parent=root['id'], data=Conv(comment))
            tree = findChildNodes(comment, comments, tree) 
    return tree

start()

