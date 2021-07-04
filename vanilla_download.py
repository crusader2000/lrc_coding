import multiprocessing
from multiprocessing import Manager, Process, Value, Array
import time
import datetime
import pickle
import random
import csv
# from pymemcache.client import base
import subprocess
import os

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_micros():
    return int((datetime.datetime.now() - epoch).total_seconds() * 1000000.0)


def add_to_queue(queue,finish):
    finish.value = False
    with open('trace.csv', mode='r') as trace_file:
        trace_reader = csv.reader(trace_file)
        data = list(trace_reader)
        queue.append(data[1][2])
        # print(datetime.datetime.now(),queue)
        for i in range(2,len(data)):
            # print(float(data[i][0])-float(data[i-1][0]))
            time.sleep(float(data[i][0])-float(data[i-1][0]))
            queue.append(data[i][2])
            print(i,datetime.datetime.now())
    finish.value = True

def download_file(name):
    bashCommand = "python3 download.py " + name
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('UTF-8')
    print(output)
    print("PROCESS COMPLETED")

def caching(queue,finish):
    print("STARTED DOWNLOADING")

    while True:
        if len(queue) == 0:
            if finish.value:
                print("NOT HERE")
                break
            else:
                time.sleep(0.1)
        file = queue.pop(0)
        print(datetime.datetime.now(),file,len(queue))
        # print(queue[:10])
        download_file(file)

if __name__ == '__main__':


    finish = Value('d', False)

    manager = Manager()
    queue = manager.list()
    print(datetime.datetime.now())
    p1 = Process(target=add_to_queue, args=(queue,finish,))
    p2 = Process(target=caching, args=(queue,finish,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

