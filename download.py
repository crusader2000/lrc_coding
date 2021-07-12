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

access_key_id = 'AKIAXJULJPQNZCGYW7H7'
secret_access_key = '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'


epoch = datetime.datetime.utcfromtimestamp(0)

failed_nodes = ["cachestorealgo1","cachestorealgo15","cachestorealgo29"] # hard code

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

def download_api_call(s3,bucket_name,object_name,file_name):
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

    regions = db_upload["aws_regions"]
    buckets = db_upload["buckets"]
    bucket_space = db_upload["bucket_space"]
    locations = db_upload["locations"]
    
    s3_conns = [] 

    for loc in regions:
        s3_conns.append(connection_S3(loc))


    for file in files:
        curr_time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        # Download Files
        for i in range(3):
            if download_api_call(s3_conns[locations[file+"_copy_"+str(i+1)][1]],locations[file+"_copy_"+str(i+1)][0],file+"_copy_"+str(i+1),file):
                break
            else:
                time.sleep(1)
        
        tb = unix_time_micros()
        time_taken = tb-ta

        db_download["download_vanilla"].append([curr_time,file,time_taken])
        
        print("Size of %s - %f"%(files,(os.path.getsize("./parts/"+file)/(1024*1024))))
        # Delete unnecessary files and folders

        if os.path.exists("./parts/"+file):
           os.remove("./parts/"+file)
    
    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
