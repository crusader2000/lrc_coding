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


def get_buckets(bucket_space):
    indices = np.argsort(bucket_space)
    return indices[:3]

def upload_api_call(s3,bucket_name,file_path,object_name):
    try:
        response = s3.upload_file(file_path, bucket_name,object_name)
    except ClientError as e:
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

    loc = db_upload["aws_region"]
    buckets = db_upload["buckets"]
    bucket_space = db_upload["bucket_space"]
    locations = db_upload["locations"]
    s3 = connection_S3(loc)

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
        print(i)
        time = datetime.datetime.now().__str__()
        if file+"_copy_1" in list(locations.keys()):
            continue

        try:
            ta = unix_time_micros()
             
            indices = get_buckets(bucket_space)
            for i,idx in enumerate(indices):
                size = os.path.getsize(path+file) 
                bucket_space[idx] = float(bucket_space[idx])+float(size/(1024*1024))
                locations[file+"_copy_"+str(i+1)] = buckets[idx]
                upload_api_call(s3,buckets[idx],path+file,file+"_copy_"+str(i+1))
                print("Uploading To - ",buckets[idx])
            
            tb = unix_time_micros()
            time_taken = tb-ta

            db_upload["upload_vanilla"].append([time,file,time_taken])
        except:
            pass
    dbfile = open('pckl_upload', 'wb')
    pickle.dump(db_upload, dbfile)
    dbfile.close()
