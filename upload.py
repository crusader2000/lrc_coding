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

access_key_id = ''
secret_access_key = '' 

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
    return indices[0]

def upload_api_call(s3,bucket_name,file_path,object_name):
    try:
        response = s3.upload_file(file_path, bucket_name,object_name)
    except ClientError as e:
        pass

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
    locations = db["locations"]
    s3 = connection_S3(loc)
    
    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        
        idx = get_buckets(bucket_space)
        size = os.path.getsize(file) 
        bucket_space[idx] = float(bucket_space[idx])+float(size/(1024*1024))
        locations[file] = buckets[idx]
        upload_api_call(s3,buckets[idx],file,file)
        
        tb = unix_time_micros()
        time_taken = tb-ta
        print("Uploading To - ",buckets[idx])

        db["upload_vanilla"].append([time,file,time_taken])
        
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()