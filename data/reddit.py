import zip as zip
import re, os
import pickle
 
def merge(filename, directory):      
    zip.unzip('reddit.zip', directory)    
    mergedConvs = []    
    for subdir, dirs, files in os.walk(directory):
        for file in files:       
            with open(os.path.join(subdir, file), 'rb') as data_file:       
                data = pickle.load(data_file)            
                for conv in data:
                    mergedConvs.append(conv)
    with open(os.path.join(directory,filename), 'wb') as fp:
        pickle.dump(mergedConvs, fp)

def unzip(dir):
    zip.unzip('reddit.zip', dir)
    
