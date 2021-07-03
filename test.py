import pickle

if __name__ == '__main__':

    # database
    # Get pickle file
        dbfile = open('pckl_download', 'rb')
        db_download = pickle.load(dbfile)
        # for k,v in db.items():
        #     print(k,v)
        dbfile.close()

        db_download["download_vanilla"] = [["Time","File Name","Time Taken (in microseconds)"]]

        dbfile = open('pckl_download', 'wb')
        pickle.dump(db_download, dbfile)
        dbfile.close()
