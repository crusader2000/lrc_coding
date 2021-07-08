import csv
from pymemcache.client import base
import pickle

client = base.Client(('localhost', 11211))

files = []
with open('trace.csv', mode='r') as trace_file:
    trace_reader = csv.reader(trace_file)
    for row in list(trace_reader):
        files.append(row[2])
    files.pop(0)

client.delete_multi(files)
for file in files:
    result = client.get(file)
    # print(file)
    if result is not None:
        print("FILE PRESENT")

dbfile = open('pckl_upload', 'rb')
db_upload = pickle.load(dbfile)
# for k,v in db.items():
#     print(k,v)
dbfile.close()
db_upload["cache_requests"] = [["Time","File Name","Cache Hit","Time Taken (in microseconds)"]]

dbfile = open('pckl_upload', 'wb')
pickle.dump(db_upload, dbfile)
dbfile.close()

dbfile = open('pckl_download', 'rb')
db_download = pickle.load(dbfile)
# for k,v in db.items():
#     print(k,v)
dbfile.close()

db_download["download_requests"] = [["Time","File Name","Files Downloaded","Num Global Blocks","Num Local Parity","Time To Download (in microseconds)","Time To Decode (in microseconds)","Total Time Taken (in microseconds)","Size"]]


dbfile = open('pckl_download', 'wb')
pickle.dump(db_download, dbfile)
dbfile.close()

