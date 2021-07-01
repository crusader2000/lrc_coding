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
import random


access_key_id = 'AKIAZFE27KY2ZF6I7E5L'
secret_access_key = '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' 

epoch = datetime.datetime.utcfromtimestamp(0)

failed_nodes = ["cachestore1","cachestore9"] # hard code

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

def download_api_call(bucket_name,object_name,file_name):
    if bucket_name in failed_nodes:
        return False
    s3.download_file(bucket_name,object_name,'./parts/'+file_name)
    return True

# Get the files needed to be encoded from command line
if __name__ == '__main__':
    
    files = sys.argv
    files.pop(0)
    print(files)

    # Get pickle file
    dbfile = open('pckl_download', 'rb')
    db_download = pickle.load(dbfile)
    dbfile.close()

    dbfile = open('pckl_upload', 'rb')
    db_upload = pickle.load(dbfile)
    dbfile.close()

    loc= db_upload["aws_region"]
    buckets= db_upload["buckets"]
    locations= db_upload["locations"]
    s3 = connection_S3(loc)

    for file in files:
        curr_time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        # Download Files
        for i in range(3):
            if download_api_call(locations[file+"_"+str(i+1)],file+"_"+str(i+1),file):
                break
            else:
                time.sleep(1)
        
        tb = unix_time_micros()
        time_taken = tb-ta

        db_download["download_vanilla"].append([curr_time,file,time_taken])
        

        # Delete unnecessary files and folders

        if os.path.exists("./parts/"+file):
            os.remove("./parts/"+file)
    
    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
