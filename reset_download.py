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