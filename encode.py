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
n = k + r # Num Code Chunks

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

def upload_api_call(s3,bucket_name,file_name):
    try:
        response = s3.upload_file(file_name, bucket_name)
    except ClientError as e:
        pass


def upload_files(s3,file):
    try:
        name,ext = file.split('.')
    except:
        name = file

    locations = {}

    processes = []

    # random allocation of buckets
    buckets = []

    for i in range(k+r):
        locations[name+"_"+str(i+1)] = bucket_name[i]
        p = multiprocessing.Process(target=upload_api_call, args=(s3,bucket_name[i],name+"_"+str(i+1),))
        p.start()
        processes.append(p)
    
    for i in range(l):
        locations[name+"_local_"+str(i+1)] = bucket_name[n+i]    
        p = multiprocessing.Process(target=upload_api_call, args=(s3,bucket_name[n+i],name+"_local_"+str(i+1),))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()

    # return locations
    return locations


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

    loc = ""
    # s3 = connection_S3(loc)
    
    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        shutil.copyfile(file,'2'+file)
        
        make_partitions(file)

        # MAKE A CODE FOR RANDOM ALLOCATION OF BUCKETS
        # location = upload_files(s3,file)
        # db["locations"].update(location)
        
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