import pickle

if __name__ == '__main__':

    # database
    # Get pickle file
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
    
    db_download = {
                    "download_requests" : [["Time","File Name","Files Downloaded","Num Global Blocks","Num Local Parity","Time To Download (in microseconds)","Time To Decode (in microseconds)","Total Time Taken (in microseconds)"]],
                            "download_vanilla" : [["Time","File Name","Time Taken (in microseconds)"]],
                                }
    dbfile = open('pckl_download', 'wb')
    pickle.dump(db_download, dbfile)
    dbfile.close()
