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

k = 6 # Num Data Chunks
r = 2 # Num Global Parity Chunks
l = 2 # Num Local Parity Chunks
n = k + r

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

def starcall_func(args):
    return download_api_call(*args)

def download_files(file_names,locations):
    processes_args = [(locations[name],name) for name in file_names]

    with multiprocessing.Pool() as pool:
        list(islice(pool.imap_unordered(starcall_func, processes_args), k))

    return

def decode_partitions(file):
    try:
        name,ext = file.split('.')
    except:
        name = file

    bashCommand = "./decode " + name
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('UTF-8')
    print(output)

    bashCommand = "xxd -plain -revert hexdump_reconstruct " +name+"_reconstruct."+ext
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return

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
        try:
            name,ext = file.split('.')
        except:
            name = file
        file_names = []
        # Download Files
        for i in range(2,n):
            file_names.append(name+"_"+str(i+1))
        download_files(file_names,locations)

        decode_partitions(file)

        tb = unix_time_micros()
        time_taken = tb-ta

        db["download_requests"].append([time,file,6,0,time_taken])


        # Delete unnecessary files and folders
        for i in range(k+r):
            if os.path.exists("parts/"+name+"_"+str(i+1)):
                os.remove("parts/"+name+"_"+str(i+1))
        for i in range(l):
           if os.path.exists("parts/"+name+"_local_"+str(i+1)):
               os.remove("parts/"+name+"_local_"+str(i+1))

        os.remove("hexdump_reconstruct")
    
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()
