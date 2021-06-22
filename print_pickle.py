import json
import pickle

dbfile = open('pckl', 'rb')
db = pickle.load(dbfile)
dbfile.close()

print(json.dumps(db, indent = 3))
