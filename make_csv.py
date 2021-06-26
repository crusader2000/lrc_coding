import pickle
import csv

if __name__ == '__main__':
    dbfile = open('pckl', 'rb')
    db = pickle.load(dbfile)
    dbfile.close()

    print("download_requests")
    with open('downloads.csv', mode='w') as download_file:
        download_writer = csv.writer(download_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db["download_requests"]:
            print(row)
            download_writer.writerow(row)
    print()
    print("upload_requests")
    with open('uploads.csv', mode='w') as upload_file:
        upload_writer = csv.writer(upload_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in db["upload_requests"]:
            print(row)
            upload_writer.writerow(row)
    print()
    print("upload_vanilla")
    for row in db["upload_vanilla"]:
        print(row)
    print()
    print("download_vanilla")
    for row in db["download_vanilla"]:
        print(row)
    print()
    print("cache_requests")
    for row in db["cache_requests"]:
        print(row)
