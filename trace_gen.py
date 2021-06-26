import csv
import requests
import re
import hashlib
import os

def cheaphash(string,length=6):
    if length<len(hashlib.sha256(string).hexdigest()):
        return hashlib.sha256(string).hexdigest()[:length]
    else:
        raise Exception("Length too long. Length of {y} when hash length is {x}.".format(x=str(len(hashlib.sha256(string).hexdigest())),y=length))

if not os.path.exists("./files"):
    os.mkdir("./files")

data = []

with open('requests.txt','r') as f:

    # first_line = f.readline()
    # start_time = float(first_line.split(' ')[1])
    # print(start_time)

    for row in f.readlines():
        row = row.strip()
        items = row.split(' ')
        items.pop(-1)
        items.pop(0)
        url = items[-1]
        # r = requests.get(url, allow_redirects=True)
        filename = url.rsplit('/', 1)[1]
        # items[1] = float(items[1])-start_time
        items.append(cheaphash(filename.encode('utf-8')))
        # open("files/"+items[-1], 'wb').write(r.content)
        data.append(items)

# print(data)

data = sorted(data, key = lambda x: float(x[0]))
# print(data)

start_time = float(data[0][0])

for row in data:
    row[0] = float(row[0]) - start_time

with open('trace.csv', mode='w') as trace_file:
    trace_writer = csv.writer(trace_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    trace_writer.writerow(["Time","URL","File_Name(Hashed)"])
    for row in data:
        print(row)
        trace_writer.writerow(row)


## Upload Trace
