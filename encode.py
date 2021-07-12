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
alpha = 3 # Score For Popular items

access_key_id = 'AKIAXJULJPQNZCGYW7H7'
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

def get_buckets(bucket_score,priority):

    if priority != '':
        indices1 = sorted([(bucket_score[i],i) for i in range(priority*10,(priority+1)*10)])
        indices2 = sorted([(bucket_score[i],i) for i in range(30) if i not in range(priority*10,(priority+1)*10)])

        random_server_indices_data = [indices1[i][1] for i in range(k)]
        random_server_indices_parity = [indices2[i][1] for i in range(r+l)]
        random_server_indices = random_server_indices_data + random_server_indices_parity
    else:
        indices = np.argsort(bucket_score)
        random_server_indices = [indices[i] for i in range(n+l)]
    
    # print("random_server_indices")
    # print(random_server_indices)
    
    # print("[buckets[idx] for idx in random_server_indices]")
    # print([buckets[idx] for idx in random_server_indices])
    # print([bucket_score[idx] for idx in random_server_indices])
    return random_server_indices

def upload_api_call(i,bucket_name,file_path,object_name):
    # try:
        response = s3_conns[i].upload_file(file_path, bucket_name,object_name)
    # except:
      #  print("NOT HERE")
      #  pass

def upload_files(s3_conns,file,locations,buckets,bucket_space,bucket_score,priority):
    try:
        name,ext = file.split('.')
    except:
        name = file


    processes_args = []

    # random allocation of buckets
    buckets_idxs = get_buckets(bucket_score,priority)
    print(buckets[idx] for idx in buckets_idxs)

    size = os.path.getsize("parts/"+name+"_"+str(1)) 
    
    for i in range(k+r):
        locations[name+"_"+str(i+1)] = buckets[buckets_idxs[i]]
        bucket_space[buckets_idxs[i]] = float(bucket_space[buckets_idxs[i]])+float(size/(1024*1024))
        processes_args.append((buckets_idxs[i]//10,buckets[buckets_idxs[i]][0],"parts/"+name+"_"+str(i+1),name+"_"+str(i+1)))
        if priority and i<k:
            bucket_score[buckets_idxs[i]] = bucket_score[buckets_idxs[i]] + alpha
        else:
            bucket_score[buckets_idxs[i]] = bucket_score[buckets_idxs[i]] + 1

    
    for i in range(l):
        locations[name+"_local_"+str(i+1)] = buckets[buckets_idxs[n+i]]
        bucket_space[buckets_idxs[n+i]] = float(bucket_space[buckets_idxs[n+i]])+float(size/(1024*1024))
        processes_args.append((buckets_idxs[n+i]//10,buckets[buckets_idxs[n+i]][0],"parts/"+name+"_local_"+str(i+1),name+"_local_"+str(i+1)))
        bucket_score[buckets_idxs[n+i]] = bucket_score[buckets_idxs[i]] + 1
    
    p = multiprocessing.Pool()
    p.starmap(upload_api_call, processes_args)

    return locations,bucket_space,bucket_score


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
            data = list(trace_reader)
            data.pop(0)
            for row in data:
                if row[3] != '':
                    files.append((str(row[2]),int(row[3])))
                else:
                    files.append((str(row[2]),''))
        path = "./files2/"
        
        print(files)

    regions = db_upload["aws_regions"]
    buckets = db_upload["buckets"]
    bucket_space = db_upload["bucket_space"]
    bucket_score = db_upload["bucket_score"]
    locations = db_upload["locations"]
    
    s3_conns = [] 

    for loc in regions:
        s3_conns.append(connection_S3(loc))
    
    count = 0
    for i,tpl in enumerate(files):

        # shutil.copyfile(file,'2'+file)
        file,priority = tpl
        try:
            name,ext = file.split('.')
        except:
            name = file

        print("-------------- %d -----------------" %(i))
        print(file,priority)
        if str(name+"_1") in list(locations.keys()):
            continue

        if count < 10:
            count = count + 1
        else:
            break
        print(name,file)
        # try:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        make_partitions(path,file)
        tb = unix_time_micros()
        # MAKE A CODE FOR RANDOM ALLOCATION OF BUCKETS
        locations,bucket_space,bucket_score = upload_files(s3_conns,file,locations,buckets,bucket_space,bucket_score,priority)
        #  print(locations,bucket_space) 
        db_upload["locations"].update(locations)
        db_upload["bucket_space"] = bucket_space
        db_upload["bucket_score"] = bucket_score
    
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
