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


access_key_id = 'AKIAZFE27KY2ZF6I7E5L'
secret_access_key = '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' 
epoch = datetime.datetime.utcfromtimestamp(0)

failed_nodes = ["cachestorers1","cachestorers9"] # hard code

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

def download_files(file_names,locations,num_files_download):
    processes_args = [(locations[name],name) for name in file_names]

    with multiprocessing.Pool(3) as pool:
        list(islice(pool.imap_unordered(starcall_func, processes_args), num_files_download))

    return

def decode_partitions(file):
    try:
        name,ext = file.split('.')
        ext = '.'+ext
    except:
        name = file
        ext = ''

    bashCommand = "./decode_rs " + name+ext
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('UTF-8')
    print(output)
    print(name)

    return

def files_downloaded(name):
    downloaded_files = os.listdir("./parts")
    global_blocks = 0
    local_blocks = 0
    for i in range(k):
        if (name+"_"+str(i+1)) in downloaded_files:
            global_blocks = global_blocks + 1
    
    for i in range(k,n):
        if (name+"_"+str(i+1)) in downloaded_files:
            local_blocks = local_blocks + 1
    return global_blocks,local_blocks

def get_files(locations,name):
    file_locations = [locations[name+"_"+str(i+1)] for i in range(n)]

    final_file_names = []
    num_parity_used = 0
    count = 0
    for i in range(n):
        if count == (k+1):
            break
        if file_locations[i] in failed_nodes:
            count = count + 1
        else:
            final_file_names.append(name+"_"+str(i+1))

    return final_file_names

# Get the files needed to be encoded from command line
if __name__ == '__main__':
    
    files = sys.argv
    files.pop(0)
    print(files)

    # Get pickle file
    dbfile = open('pckl_download', 'rb')
    db_download = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()

    dbfile = open('pckl_upload', 'rb')
    db_upload = pickle.load(dbfile)
    # for k,v in db.items():
    #     print(k,v)
    dbfile.close()
    
    loc= db_upload["aws_region"]
    buckets= db_upload["buckets"]
    locations= db_upload["locations"]
    s3 = connection_S3(loc)

    for file in files:
        time = datetime.datetime.now().__str__()
        ta = unix_time_micros()
        try:
            name,ext = file.split('.')
        except:
            name = file

        file_names = get_files(locations,name)

        # Download Files
        download_files(file_names,locations,len(file_names))
        
        tb = unix_time_micros()

        decode_partitions(file)

        tc = unix_time_micros()

        time_to_download = tb-ta
        time_to_decode = tc-tb
        total_time_taken = tc-ta

        global_blocks,local_blocks = files_downloaded(name)
        db_download["download_requests"].append([time,file,os.listdir("./parts"),global_blocks,local_blocks,time_to_download,time_to_decode,total_time_taken])
        # print(db_download["download_requests"]) 

        # Delete unnecessary files and folders
        for i in range(k+r):
            if os.path.exists("parts/"+name+"_"+str(i+1)):
                os.remove("parts/"+name+"_"+str(i+1))

        if os.path.exists("hexdump_reconstruct"):
            os.remove("hexdump_reconstruct")
    
    print("PRNITNG DB") 
    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
