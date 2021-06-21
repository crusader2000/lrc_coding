import boto3
import boto3.session
import datetime
import time
import numpy as np
import os
import csv
import sys
import subprocess
import shutil
import multiprocessing
import pickle

k = 6 # Num Data Chunks
r = 2 # Num Global Parity Chunks
l = 2 # Num Local Parity Chunks
n = k + r # Num Code Chunks

access_key_id = ""
secret_access_key = ""

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

def make_partitions(file):
    try:
        name,ext = file.split('.')
    except:
        name = file

    bashCommand = "xxd -plain " +file+" hexdump"

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    bashCommand = "./encode " + name

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

    output, error = process.communicate()
    output = output.decode('UTF-8')

    print(output)
    return

def get_buckets(bucket_space):
    indices = np.flip(numpy.argsort(myList))
    print(indices)
    random_server_indices = random.sample(indices[:(n+l+3)],n+l)
    print(random_server_indices)
    print([buckets[idx] for idx in random_server_indices])
    return random_server_indices

def upload_api_call(s3,bucket_name,file_path,object_name):
    try:
        response = s3.upload_file(file_path, bucket_name,object_name)
    except ClientError as e:
        pass

def upload_files(s3,file,locations,buckets,bucket_space):
    try:
        name,ext = file.split('.')
    except:
        name = file


    processes_args = []

    # random allocation of buckets
    buckets_idxs = get_buckets(bucket_space)
    
    size = os.path.getsize("parts/"+name+"_"+str(1)) 

    for i in range(k+r):
        locations[name+"_"+str(i+1)] = buckets[buckets_idxs[i]]
        bucket_space[buckets_idxs[i]] = bucket_space[buckets_idxs[i]] + size
        processes_args.append((s3,buckets[buckets_idxs[i]],"parts/"+name+"_"+str(i+1),name+"_"+str(i+1)))
        # p = multiprocessing.Process(target=upload_api_call, 
        #     args=(s3,buckets[buckets_idxs[i]],"parts/"+name+"_"+str(i+1),name+"_"+str(i+1),))
        # p.start()
        # processes.append(p)
    
    for i in range(l):
        locations[name+"_local_"+str(i+1)] = buckets[buckets_idxs[n+i]]    
        bucket_space[buckets_idxs[n+i]] = bucket_space[buckets_idxs[n+i]] + size
        processes_args.append((s3,buckets[buckets_idxs[n+i]],"parts/"+name+"_local_"+str(i+1),name+"_local_"+str(i+1)))
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
    dbfile = open('pckl', 'rb')
    db = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()

    files = sys.argv
    files.pop(0)
    print(files)

    loc = db["aws_region"]
    buckets = db["buckets"]
    bucket_space = db["bucket_space"]
    # s3 = connection_S3(loc)
    
    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        shutil.copyfile(file,'2'+file)
        
        make_partitions(file)

        # MAKE A CODE FOR RANDOM ALLOCATION OF BUCKETS
        # locations,bucket_space = upload_files(s3,file)
        # db["locations"].update(location)
        # db["bucket_space"] = bucket_space
        
        tb = unix_time_micros()
        time_taken = tb-ta

        db["upload_requests"].append([time,file,time_taken])

        # Delete unnecessary files and folders
        # for i in range(k+r):
        #     if os.path.exists("parts/"+name+"_"+str(i+1)):
        #         os.remove(name+"_"+str(i+1))
        # for i in range(l):
        #     if os.path.exists("parts/"+name+"_local_"+str(i+1)):
        #         os.remove(name+"_local_"+str(i+1))

        os.remove('2'+file)
        # os.remove(file)
        os.remove("hexdump")
    
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()