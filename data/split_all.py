import argparse
import random
import pickle, os

def saveData(enc, dec, data):
   
    enc_dat, dec_dat = seperateData(data)        
    #print(dec_dat)
    #exit()    
    with open(enc, 'wb') as file:
        for line in enc_dat:
            file.write(line+'\n')
    with open(dec, 'wb') as file:
        for line in dec_dat:
            file.write(line+'\n')

def seperateData(data):
    i = 0    
    enc = []
    dec = []   
    for conv in data:    
        for line in conv:
            if i % 2 == 0:
                enc.append(line)
            else:
                dec.append(line)
            i+=1
    return enc, dec     


parser = argparse.ArgumentParser()
parser.add_argument('--f', help='The name of the directory')
parser.add_argument('--t', type=int, help='Percentage of data for testing, the rest will be used for training')
parser.add_argument('--d', help='Name of directory to put created files into')
args = parser.parse_args()

if args.t < 0 and args.f > 100:
    print('Error: Invalid percentage, must be between 0 and 100')
    exit()

train_data = []
test_data = []

for subdir, dirs, files in os.walk(args.f):
    for file in files:
        print('Splitting data file...', file)        
        with open(os.path.join(subdir, file), 'rb') as data_file:       
            data = pickle.load(data_file)            
            #print data           
            for conv in data:
                rnd = random.randint(1,100)
                if rnd <  args.t:
                    #print('Added to testing with rnd num:', rnd)
                    test_data.append(conv)
                else:      
                    train_data.append(conv)  
                    
 

print('Data split...')
if not os.path.exists(args.d):
    os.makedirs(args.d)
try:
    saveData(args.d+'/test.enc', args.d+'/test.dec', test_data)
    saveData(args.d+'/train.enc', args.d+'/train.dec', train_data)
except IOError:
    print('Directory doesnt exist and failed to be created!')


