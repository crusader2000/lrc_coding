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

bucket_name = ["","","","","","",""]
location = ["","","","","","",""]

k = 6 # Num Data Chunks
r = 2 # Num Global Parity Chunks
l = 2 # Num Local Parity Chunks

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)

def connection_S3(loc):
    s3 = boto3.client('s3',aws_access_key_id = access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=loc)
    return s3

def download_api_call(s3,bucket_name,file_name):
    s3.download_file(bucket_name,file_name,'./parts/'+file_name)    

def download_files(s3,file_names,locations):
    p = multiprocessing.Pool()
    processes_args = []

    for name in file_names:
        processes_args.append((s3,locations[name],name))
        # p = multiprocessing.Process(target=download_api_call, args=(s3,locations[name],name,))
        # p.start()
        # processes.append(p)

    p.starmap(download_api_call, processes_args)
    # for p in processes:
    #     p.join()
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
    location = db["locations"]
    # s3 = connection_S3(loc)

    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        # Download Files
        # download_files(s3,name,locations)

        decode_partitions(file)

        tb = unix_time_micros()
        time_taken = tb-ta

        db["download_requests"].append([time,file,0,0,time_taken])

        # Delete unnecessary files and folders
        # for i in range(k+r):
        #     if os.path.exists(name+"_"+str(i+1)):
        #         os.remove(name+"_"+str(i+1))
        # for i in range(l):
        #     if os.path.exists(name+"_local_"+str(i+1)):
        #         os.remove(name+"_local_"+str(i+1))

        os.remove("hexdump_reconstruct")
    
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()