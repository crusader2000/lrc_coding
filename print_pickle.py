import json
import pickle

dbfile = open('pckl_upload', 'rb')
db_upload = pickle.load(dbfile)
dbfile.close()

print(json.dumps(db_upload, indent = 3))


dbfile = open('pckl_download', 'rb')
db_download = pickle.load(dbfile)
dbfile.close()

print(json.dumps(db_download, indent = 3))

