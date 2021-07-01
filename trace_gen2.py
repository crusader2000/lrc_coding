import csv
import requests
import re
import hashlib
import os
import itertools

def cheaphash(string,length=6):
    if length<len(hashlib.sha256(string).hexdigest()):
        return hashlib.sha256(string).hexdigest()[:length]
    else:
        raise Exception("Length too long. Length of {y} when hash length is {x}.".format(x=str(len(hashlib.sha256(string).hexdigest())),y=length))

if not os.path.exists("./files"):
    os.mkdir("./files")

urls = []

with open('urls.csv', mode='r') as url_file:
    url_reader = csv.reader(url_file)
    urls = list(itertools.chain.from_iterable(list(url_reader)))

len_urls = len(urls)
# print(urls)
with open('requests.txt','r') as f:

    # first_line = f.readline()
    # start_time = float(first_line.split(' ')[1])
    # print(start_time)
    count = 0
    for row in f.readlines():
        row = row.strip()
        items = row.split(' ')
        items.pop(-1)
        items.pop(0)
        dead_url = items[-1] # Only using this to create new filenames
        filename = dead_url.rsplit('/', 1)[1]
        items.append(cheaphash(filename.encode('utf-8')))
        if not os.path.exists("files/"+filename):
            r = requests.get(urls[count % len_urls], allow_redirects=True)
            open("files/"+items[-1], 'wb').write(r.content)
        data.append(items)
        count = count + 1
        print(count)

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
