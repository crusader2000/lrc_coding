import multiprocessing
from multiprocessing import Manager, Process, Value, Array
import time
import datetime
import pickle
import random 
import csv
from pymemcache.client import base

def add_to_queue(queue,finish):
    finish = False
    with open('trace.csv', mode='r') as trace_file:
        trace_reader = csv.reader(trace_file)
        data = list(trace_reader)
        queue.append(data[1][-1])
        print(datetime.datetime.now(),queue)
        for i in range(2,len(data)):
            print(float(data[i][0])-float(data[i-1][0]))
            time.sleep(float(data[i][0])-float(data[i-1][0]))
            queue.append(data[i][-1])
            print(i,datetime.datetime.now(),queue)
    finish = True

def download_file(name):
    bashCommand = "python3 decode.py " + name
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('UTF-8')
    # print(output)

def caching(queue,finish):
    client = base.Client(('localhost', 11211))

    dbfile = open('pckl', 'rb')
    db = pickle.load(dbfile)
    requests = db["cache_requests"]
    dbfile.close()

    while True:
        if not len(queue):
            if finish:
                break
            else:
                time.sleep(0.1)
        curr_time = datetime.datetime.now()
        ta = unix_time_micros()
        file = queue.pop(0)
        result = client.get(file)
        cache_hit = 1
        if result is None:
            cache_hit = 0
            download_file(file)
            
            f = open(file+"_reconstruct",'rb')
            client.set(file, f.read())
            f.close()
            
            os.remove(file+"_reconstruct")
        tb = unix_time_micros()
        
        requests.append([curr_time,file,cache_hit,tb-ta])

    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()
       

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

    