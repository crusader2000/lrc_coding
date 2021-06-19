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

bucket_name = ["","","","","","",""]
location = ["","","","","","",""]

k = 6 # Num Data Chunks
r = 2 # Num Global Parity Chunks
l = 2 # Num Local Parity Chunks

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

def upload_files(s3,file):
    try:
        name,ext = file.split('.')
    except:
        name = file

    locations = {}

    # random allocation of buckets
    for i in range(k+r):
        locations[name+"_"+str(i+1)] = bucket_name[i]    
        try:
            response = s3.upload_file(name+"_"+str(i+1), bucket_name[i])
        except ClientError as e:
            pass
    
    for i in range(l):
        locations[name+"_local_"+str(i+1)] = bucket_name[i]    
        try:
            response = s3.upload_file(name+"_local_"+str(i+1), bucket_name[i])
        except ClientError as e:
            pass

    # return locations
    return locations


# Get the files needed to be encoded from command line
if __name__ == '__main__':
    
    files = sys.argv
    files.pop(0)
    print(files)

    loc = ""
    # s3 = connection_S3(loc)
    
    for file in files:
        shutil.copyfile(file,'2'+file)
        
        make_partitions(file)

        # MAKE A CODE FOR RANDOM ALLOCATION OF BUCKETS
        # upload_files(s3,file)

        # Delete unnecessary files and folders
        # for i in range(k+r):
        #     if os.path.exists(name+"_"+str(i+1)):
        #         os.remove(name+"_"+str(i+1))
        # for i in range(l):
        #     if os.path.exists(name+"_local_"+str(i+1)):
        #         os.remove(name+"_local_"+str(i+1))

        os.remove('2'+file)
        # os.remove(file)
        os.remove("hexdump")
