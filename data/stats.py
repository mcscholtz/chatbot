import argparse
import pickle, os
from matplotlib import pyplot as plt

def createPlot(file, dir, input_list, output_list, input_max_len_file, output_max_len_file, bucket_count):
    title = "Plot of " + file
    txt = "Number of datapoints: " + str(len(input_list)) + "\nMax output length: " + output_max_len_file + "\nMax input length: " + input_max_len_file + "\n"
    for i in range(len(bucket_count)):
            #print("Bucket", i, "Total: ", bucket_count[i])
            txt+= ("B"+ str(i) + ":" + str(bucket_count[i])+"  ")
    fig = plt.figure(1)
    ax1 = fig.add_axes((.1,.4,.8,.5))
    ax1.scatter(input_list,output_list, s=2, c='red')
    fig.text(.1,.1,txt, fontsize=12)
    ax1.set_title(title)
    ax1.set_ylabel('Input Word Count')
    ax1.set_xlabel('Output Word Count')
    
    filename = file.split('.')[0]
    filename = os.path.join(dir,file + '.png')
    print("Saved graph..",filename)
    plt.savefig(filename)
    plt.clf()

def parse(file, dir):
    bucket_count = [0,0,0,0,0]
    bucket_size = [(3, 3), (6, 6), (9, 9), (12, 12), (15,15)]
    #Add more stats, such as datapoints per bucket
    input_max_len_file = 0
    output_max_len_file = 0
    input_list = []
    output_list = []
    with open(os.path.join(dir,file), 'rb') as fp:
        itemlist = pickle.load(fp) 
        for conversation in itemlist:
            i=0
            prev=0
            for line in conversation:
                length = len(line.split())
                if i % 2 == 0:
                    #if even, then input
                    if length > input_max_len_file:
                        input_max_len_file = length
                    input_list.append(length)
                    if prev > 0:                    
                        input = length
                        output = prev
                else:
                    if length > output_max_len_file:
                        output_max_len_file = length
                    output_list.append(length)
                    if prev > 0:                    
                        input = length
                        output = prev
                i+=1
                            #Calc more stats here
                if prev > 0:
                    if(input <= bucket_size[0][0] and output <= bucket_size[0][1]):
                        bucket_count[0] += 1
                    elif(input > bucket_size[0][0] and output > bucket_size[0][1] and input <= bucket_size[1][0] and output <= bucket_size[1][1]):
                                    bucket_count[1] += 1
                    elif(input > bucket_size[1][0] and output > bucket_size[1][1] and input <= bucket_size[2][0] and output <= bucket_size[2][1]):
                                    bucket_count[2] += 1
                    elif(input > bucket_size[2][0] and output > bucket_size[2][1] and input <= bucket_size[3][0] and output <= bucket_size[3][1]):
                                    bucket_count[3] += 1
                    elif(input > bucket_size[3][0] and output > bucket_size[3][1] and input <= bucket_size[4][0] and output <= bucket_size[4][1]):
                                    bucket_count[4] += 1
                prev = length
        #print(len(input_list))
        #print(len(output_list))
        
        #saveStats(file, input_list, output_list)
        for i in range(len(bucket_size)):
            print("Bucket", i, "Total: ", bucket_count[i])
        createPlot(file, dir, input_list, output_list, str(input_max_len_file), str(output_max_len_file), bucket_count)

#parser = argparse.ArgumentParser()
#parser.add_argument('--f', help='Name of the file to generate stats for')
#parser.add_argument('--d', help='The directory where everything will happen in')
#args = parser.parse_args()

      
#parse(args.f, args.d)
      
