import boto3
import boto3.session
import datetime
import time
import random
import numpy as np
import os
import csv
import sys
import subprocess
import shutil
import multiprocessing
import pickle
from time import sleep

k = 6 # Num Data Chunks
r = 2 # Num Global Parity Chunks
l = 2 # Num Local Parity Chunks
n = k + r # Num Code Chunks


access_key_id = 'AKIAZFE27KY2ZF6I7E5L'
secret_access_key = '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' 
epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

def make_partitions(path,file):
    try:
        name,ext = file.split('.')
    except:
        name = file
    try:
        shutil.copy(path+file,file)
    except:
        pass

    bashCommand = "./encode " + file

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

    output, error = process.communicate()
    output = output.decode('UTF-8')

    os.remove(file)
    print(output)
    return

def get_buckets(bucket_space):
    indices = np.argsort(bucket_space)
    print(indices)
    print([bucket_space[idx] for idx in indices])
    random_server_indices = random.sample([indices[i] for i in range(n+l+1)],n+l)
    
    print("random_server_indices")
    print(random_server_indices)
    
    print("[buckets[idx] for idx in random_server_indices]")
    print([buckets[idx] for idx in random_server_indices])
    print([bucket_space[idx] for idx in random_server_indices])
    return random_server_indices

def upload_api_call(bucket_name,file_path,object_name):
    try:
        response = s3.upload_file(file_path, bucket_name,object_name)
    except ClientError as e:
        print("NOT HERE")
        pass

def upload_files(file,locations,buckets,bucket_space):
    try:
        name,ext = file.split('.')
    except:
        name = file


    processes_args = []

    # random allocation of buckets
    buckets_idxs = get_buckets(bucket_space)
    print(buckets[idx] for idx in buckets_idxs)

    size = os.path.getsize("parts/"+name+"_"+str(1)) 
    
    for i in range(k+r):
        locations[name+"_"+str(i+1)] = buckets[buckets_idxs[i]]
        bucket_space[buckets_idxs[i]] = float(bucket_space[buckets_idxs[i]])+float(size/(1024*1024))
        processes_args.append((buckets[buckets_idxs[i]],"parts/"+name+"_"+str(i+1),name+"_"+str(i+1)))
        # p = multiprocessing.Process(target=upload_api_call, 
        #     args=(s3,buckets[buckets_idxs[i]],"parts/"+name+"_"+str(i+1),name+"_"+str(i+1),))
        # p.start()
        # processes.append(p)
    
    for i in range(l):
        locations[name+"_local_"+str(i+1)] = buckets[buckets_idxs[n+i]]    
        bucket_space[buckets_idxs[n+i]] = float(bucket_space[buckets_idxs[n+i]])+float(size/(1024*1024))
        processes_args.append((buckets[buckets_idxs[n+i]],"parts/"+name+"_local_"+str(i+1),name+"_local_"+str(i+1)))
        # p = multiprocessing.Process(target=upload_api_call, 
        #     args=(s3,buckets[buckets_idxs[n+i]],"parts/"+name+"_local_"+str(i+1),name+"_local_"+str(i+1),))
        # p.start()
        # processes.append(p)
    p = multiprocessing.Pool()
    p.starmap(upload_api_call, processes_args)
    # for p in processes:
    #     p.join()

    # return locations
    return locations,bucket_space


# Get the files needed to be encoded from command line
if __name__ == '__main__':
    
    # Get pickle file
    dbfile = open('pckl_upload', 'rb')
    db_upload = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()

    read_from_cmdline = False
    path = "./"
    
    if read_from_cmdline:
        files = sys.argv
        files.pop(0)
        path = "./"
        print(files)
    else:
        files = []
        with open('trace.csv', mode='r') as trace_file:
            trace_reader = csv.reader(trace_file)
            for row in list(trace_reader):
                files.append(str(row[-1]))
        files.pop(0)
        path = "./files2/"
        
        print(files)


    loc = db_upload["aws_region"]
    buckets = db_upload["buckets"]
    bucket_space = db_upload["bucket_space"]
    locations = db_upload["locations"]
    s3 = connection_S3(loc)
    
    count = 0
    for i,file in enumerate(files):

        # shutil.copyfile(file,'2'+file)
        
        try:
            name,ext = file.split('.')
        except:
            name = file
        print("-------------- %d  -----------------" %(i))
        if str(name+"_1") in list(locations.keys()):
            continue

        if count < 10:
            count = count + 1
        else:
            break
        print(name,file)
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        make_partitions(path,file)
        tb = unix_time_micros()
        # MAKE A CODE FOR RANDOM ALLOCATION OF BUCKETS
        locations,bucket_space = upload_files(file,locations,buckets,bucket_space)
        #  print(locations,bucket_space) 
        db_upload["locations"].update(locations)
        db_upload["bucket_space"] = bucket_space

        tc = unix_time_micros()

        time_to_encode = tb-ta
        time_to_upload = tc-tb
        total_time_taken = tc-ta

        db_upload["upload_requests"].append([time,file,time_to_encode,time_to_upload,total_time_taken])

        # Delete unnecessary files and folders
        for i in range(k+r):
            if os.path.exists("parts/"+name+"_"+str(i+1)):
                os.remove("parts/"+name+"_"+str(i+1))
        for i in range(l):
            if os.path.exists("parts/"+name+"_local_"+str(i+1)):
                os.remove("parts/"+name+"_local_"+str(i+1))

    dbfile = open('pckl_upload', 'wb')
    pickle.dump(db_upload, dbfile)
    dbfile.close()
