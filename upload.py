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

def get_buckets(bucket_space):
    indices = np.argsort(bucket_space)
    return indices[:3]

def upload_api_call(s3,bucket_name,file_path,object_name):
    try:
        response = s3.upload_file(file_path, bucket_name,object_name)
    except:
        pass

if __name__ == '__main__':
    
    # Get pickle file
    dbfile = open('pckl_upload', 'rb')
    db_upload = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()

    files = sys.argv
    files.pop(0)
    print(files)

    regions = db_upload["aws_regions"]
    buckets = db_upload["buckets"]
    bucket_space = db_upload["bucket_space"]
    locations = db_upload["locations"]
    
    s3_conns = [] 

    for loc in regions:
        s3_conns.append(connection_S3(loc))

    read_from_cmdline = False
    path = "./"
    
    if read_from_cmdline:
        files = sys.argv
        files.pop(0)
        path = "./"
        print(files)
    else:
        files = []
        with open('./trace.csv', mode='r') as trace_file:
            trace_reader = csv.reader(trace_file)
            for row in list(trace_reader):
                files.append(str(list(row)[-1]))
        files.pop(0)
        path = "./files2/"

        print(files)

    for i,file in enumerate(files):
            print(i,file)
            time = datetime.datetime.now().__str__()
        # try:
            ta = unix_time_micros()
            if file+"_copy_1" in list(locations.keys()):
                continue
            indices = get_buckets(bucket_space)
            for i,idx in enumerate(indices):
                size = os.path.getsize(path+file) 
                bucket_space[idx] = float(bucket_space[idx])+float(size/(1024*1024))
                locations[file+"_copy_"+str(i+1)] = buckets[idx]
                upload_api_call(s3_conns[idx//10],buckets[idx],path+file,file+"_"+str(i+1))
                print("Uploading To - ",buckets[idx])
            
            tb = unix_time_micros()
            time_taken = tb-ta

            db_upload["upload_vanilla"].append([time,file,time_taken])
        # except:
        #     pass
            
    dbfile = open('pckl_upload', 'wb')
    pickle.dump(db_upload, dbfile)
    dbfile.close()
