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
from itertools import islice

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

def download_api_call(bucket_name,file_name):
    s3.download_file(bucket_name,file_name,'./parts/'+file_name)    

# Get the files needed to be encoded from command line
if __name__ == '__main__':
    
    files = sys.argv
    files.pop(0)
    print(files)

    # Get pickle file
    dbfile = open('pckl', 'rb')
    db = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()

    loc = db["aws_region"]
    buckets = db["buckets"]
    bucket_space = db["bucket_space"]
    locations = db["locations"]
    s3 = connection_S3(loc)

    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        # Download Files
        download_api_call(locations[file],file)
        
        tb = unix_time_micros()
        time_taken = tb-ta

        db["download_vanilla"].append([time,file,time_taken])
        

        # Delete unnecessary files and folders

        if os.path.exists("parts/"+file):
            os.remove("parts/"+file)
    
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()
