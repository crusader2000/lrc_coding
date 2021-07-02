import csv
from pymemcache.client import base
import pickle

client = base.Client(('localhost', 11211))

files = []
with open('trace.csv', mode='r') as trace_file:
    trace_reader = csv.reader(trace_file)
    for row in list(trace_reader):
        files.append(row[-1])
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
