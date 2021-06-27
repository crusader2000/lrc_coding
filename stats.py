import csv

with open('trace.csv', mode='r') as trace_file:
    trace_reader = csv.reader(trace_file)
    data = list(trace_reader)
    print("NUMBER OF REQUESTS PER SEC - ",(len(data)-1)/float(data[-1][0]))
    print("Total Number of Requests - ",(len(data)-1))
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
