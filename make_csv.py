import pickle
import csv

if __name__ == '__main__':
    dbfile = open('pckl_upload', 'rb')
    db_upload = pickle.load(dbfile)
    dbfile.close()

    dbfile = open('pckl_download', 'rb')
    db_download = pickle.load(dbfile)
    dbfile.close()

    print("download_requests")
    with open('downloads.csv', mode='w') as download_file:
        download_writer = csv.writer(download_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db_download["download_requests"]:
            print(row)
            download_writer.writerow(row)
    print()
    print("upload_requests")
    with open('uploads.csv', mode='w') as upload_file:
        upload_writer = csv.writer(upload_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db_upload["upload_requests"]:
            print(row)
            upload_writer.writerow(row)
    print()
    print("upload_vanilla")
    for row in db_upload["upload_vanilla"]:
        print(row)
    print()
    print("download_vanilla")
    with open('download_vanilla.csv', mode='w') as cache_req_file:
        cache_writer = csv.writer(cache_req_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db_download["download_vanilla"]:
            print(row)
            cache_writer.writerow(row)
    print()
    print("cache_requests - ",len(db_upload["cache_requests"]))
    with open('cache_req.csv', mode='w') as cache_req_file:
        cache_writer = csv.writer(cache_req_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db_upload["cache_requests"]:
            print(row)
            cache_writer.writerow(row)
