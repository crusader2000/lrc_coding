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

def download_api_call(s3,file_name):
    s3.download_file(bucket_name,file_name,'./parts/'+file_name)    

def download_files(s3,name,locations):
    processes = []
    for x in calls:
        p = multiprocessing.Process(target=download_api_call, args=(s3,file_name,))
        processes.append(x)
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

    loc = ""
    # s3 = connection_S3(loc)

    for file in files:
        
        # Download Files
        # download_files(s3,name,locations)

        decode_partitions(file)

        # Delete unnecessary files and folders
        # for i in range(k+r):
        #     if os.path.exists(name+"_"+str(i+1)):
        #         os.remove(name+"_"+str(i+1))
        # for i in range(l):
        #     if os.path.exists(name+"_local_"+str(i+1)):
        #         os.remove(name+"_local_"+str(i+1))

        os.remove("hexdump_reconstruct")