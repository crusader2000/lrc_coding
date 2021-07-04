import json
import pickle

dbfile = open('pckl_upload', 'rb')
db_upload = pickle.load(dbfile)
dbfile.close()

# print(json.dumps(db_upload, indent = 3))

for key in list(db_upload.keys()):
    print(key)
    for row in db_upload[key]:
        print(json.dumps(row, indent = 3))
    print()

dbfile = open('pckl_download', 'rb')
db_download = pickle.load(dbfile)
dbfile.close()

# print(json.dumps(db_download, indent = 3))
print(db_upload["locations"])
