import pickle

if __name__ == '__main__':
    # database
    db = {
        "locations" : {
            "test" : "location_none"
        },
        "upload_requests" : [["Time","File Name","Time Taken (in microseconds)"]],
        "download_requests" : [["Time","File Name","Num Global","Num Parity","Time Taken (in microseconds)"]],
    }
  
    # Its important to use binary mode
    dbfile = open('pckl', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()