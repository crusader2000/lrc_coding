import json
import pickle

dbfile = open('pckl_upload', 'rb')
db_upload = pickle.load(dbfile)
dbfile.close()

# print(json.dumps(db_upload, indent = 3))

# for key in list(db_upload.keys()):
#     print(key)
#     for row in db_upload[key]:
#         print(json.dumps(row, indent = 3))
#     print()

dbfile = open('pckl_download', 'rb')
db_download = pickle.load(dbfile)
dbfile.close()

# print(json.dumps(db_download, indent = 3))
# print(db_upload["locations"])
# print(len(db_upload["locations"].keys()))

files = {}

for k,v in db_upload["locations"].items():
    try:
        files[v[0]].append(k)
    except:
        files[v[0]] = [k]

# for i in range(30):
#     try:
#         print("cachestorealgo"+str(i))
#         print(files["cachestorealgo"+str(i)])
#         print()
#         print()
#     except:
#         pass

for i in range(30):
    parity_count = 0

    try:
        # print("cachestorealgo"+str(i),len(files["cachestorealgo"+str(i)]),len(set(files["cachestorealgo"+str(i)])))
        for f in files["cachestorealgo"+str(i)]:
            if f[6:] in ["_7","_8","_local_1","_local_2"]:
                parity_count = parity_count + 1
        # print(files["cachestorealgo"+str(i)])
        print("cachestorealgo"+str(i),parity_count,len(files["cachestorealgo"+str(i)])-parity_count)
        # print()
        # print()
    except:
        pass
