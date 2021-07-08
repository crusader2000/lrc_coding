import csv
import requests
import re
import hashlib
import os
import itertools
import shutil

def cheaphash(string,length=6):
    if length<len(hashlib.sha256(string).hexdigest()):
        return hashlib.sha256(string).hexdigest()[:length]
    else:
        raise Exception("Length too long. Length of {y} when hash length is {x}.".format(x=str(len(hashlib.sha256(string).hexdigest())),y=length))

if not os.path.exists("./files"):
    os.mkdir("./files")

if not os.path.exists("./files2"):
    os.mkdir("./files2")

urls = []
files_available = []

with open('urls.csv', mode='r') as url_file:
      url_reader = csv.reader(url_file)
      urls = list(itertools.chain.from_iterable(list(url_reader)))
      for url in urls:
          print(url)
          filename = url.rsplit('/', 1)[1]
          if not os.path.exists("files/"+filename):
              r = requests.get(url, allow_redirects=True)
              open("files/"+filename, 'wb').write(r.content)
          files_available.append(filename)

len_files = len(files_available)
data = []
# print(urls)
files_dict = {}
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
        if not os.path.exists("files2/"+filename):
             shutil.copy("files/"+files_available[count % len_files], "files2/"+items[-1])
        data.append(items)
        count = count + 1
        print(count)
        try:
            files_dict[items[-1]] = files_dict[items[-1]] + 1
        except:
            files_dict[items[-1]] = 1


for i in range(len(data)):
    #if files_dict[data[i][2]] > 1:
     #   data[i].append(0)
    #else:
        data[i].append(None)

# print(data)

data = sorted(data, key = lambda x: float(x[0]))
# print(data)

start_time = float(data[0][0])

for row in data:
    row[0] = float(row[0]) - start_time

with open('trace.csv', mode='w') as trace_file:
    trace_writer = csv.writer(trace_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    trace_writer.writerow(["Time","URL","File_Name(Hashed)","Priority"])
    for row in data:
        print(row)
        trace_writer.writerow(row)

