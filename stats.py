import csv
import os
import pickle

with open('trace.csv', mode='r') as trace_file:
    trace_reader = csv.reader(trace_file)
    data = list(trace_reader)
    print("NUMBER OF REQUESTS PER SEC - ",(len(data)-1)/float(data[-1][0]))
    print("Total Number of Requests - ",(len(data)-1))

files = list(os.listdir("files2/"))
dir_size = 0
for file in files:
    dir_size = dir_size + os.path.getsize("files2/"+file)
#print("Average File Size - %f MBs" %(dir_size/(1024*1024*len(files))))

print("-----------------------------------------------")
print("Coding")
print("-----------------------------------------------")
with open('cache_req.csv',mode='r') as cache_req_file:
    cache_req_reader = csv.reader(cache_req_file)
    data = list(cache_req_reader)
    num_cache_hit = 0
    total_latency = 0
    
    for i in range(2,len(data)):
        num_cache_hit = num_cache_hit + int(data[i][2])
        total_latency = total_latency + float(int(data[i][3])/1000000)

    print("Average Latency (sec /req) - ",total_latency/(len(data)-1))
    print("Total Cache Hits - ",num_cache_hit)

with open('downloads.csv',mode='r') as downloads_file:
    downloads_reader = csv.reader(downloads_file)
    data = list(downloads_reader)
    decoding_latency = 0
    downloading_latency = 0
    
    for i in range(2,len(data)):
        downloading_latency = downloading_latency + float(int(data[i][5])/1000000)
        decoding_latency = decoding_latency + float(int(data[i][6])/1000000)

    print("Average Downloading Latency (sec /req) - ",downloading_latency/(len(data)-1))
    print("Average Decoding Latency (sec /req) - ",decoding_latency/(len(data)-1))
print()

dbfile = open('pckl_upload', 'rb')
db_upload = pickle.load(dbfile)
dbfile.close()

dbfile = open('pckl_download', 'rb')
db_download = pickle.load(dbfile)
dbfile.close()

locations = db_upload["locations"]

download_reqs = db_download["download_requests"]
bucket_score = db_upload["bucket_score"]

num_requests = {}
traffic = {}
files = {}

for i in range(1,len(download_reqs)):
    files_downloaded = list(download_reqs[i][2])
    # print(files_downloaded)
    for file in files_downloaded:
            try:
                num_requests[locations[file][0]] = num_requests[locations[file][0]] + 1
                traffic[locations[file][0]] =  traffic[locations[file][0]] + float(download_reqs[i][8])
                files[locations[file][0]].append(file) 
            except:
                num_requests[str(locations[file][0])] = 1
                traffic[locations[file][0]] = float(download_reqs[i][8])
                files[locations[file][0]] = [file] 

print("NUM REQUESTS")
for i in range(30):
    x = "cachestoregeo"+str(i)
    try:
        print(x,num_requests[x])
    except:
        print(x,0)
print("Stadard Deviation",np.std(list(num_requests.values())))
print()
print()
print("TRAFFIC (in MBs)")
for i in range(30):
    x = "cachestoregeo"+str(i)
    try:
        print(x,traffic[x])
    except:
        print(x,0)
print("Stadard Deviation",np.std(list(traffic.values())))
print()
print()
print()


for i in range(30):
    parity_count = 0

    try:
        print("cachestorealgo"+str(i),len(files["cachestorealgo"+str(i)]),len(set(files["cachestorealgo"+str(i)])))
        for f in files["cachestorealgo"+str(i)]:
            if f[6:] in ["_7","_8","_local_1","_local_2"]:
                parity_count = parity_count + 1
        # print(files["cachestorealgo"+str(i)])
        print(parity_count,len(files["cachestorealgo"+str(i)])-parity_count)
        print()
        print()
    except:
        pass
print("-----------------------------------------------")
print("Vanilla Download")
print("-----------------------------------------------")
with open('download_vanilla.csv',mode='r') as download_vanilla_file:
    download_vanilla_reader = csv.reader(download_vanilla_file)
    data = list(download_vanilla_reader)
    total_latency = 0
    
    for i in range(2,len(data)):
        total_latency = total_latency + float(int(data[i][2])/1000000)

    print("Average Latency (sec /req) - ",total_latency/(len(data)-1))

