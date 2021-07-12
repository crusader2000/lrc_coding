Repository containing codes w.r.t. MITACS Internship

### Locally Recoverable Codes
This is a coding technique used for Error Correction in Data Centers. It is used in Azure Storage. Ceph, an open source storage system, has plugins which allow using LRC in case of node failures.

### ISAL
Run the following command to clone ISA github repo in libs directory
```
bash ./libs/get_libs.bash
```
If installation fails, Go to ``libs/isa-l/README`` and follow the instructions present based on your OS.

### Setup Commands
```
cmake CMakeLists.txt
make
python3 setup.py
```


### Encoding of Files
The files are first converted to a hexfile using the ```xxd``` command
Use the following command to turn any file into a hexdump
```
python3 main.py
```

To get back the original file, use the following command. It will produce a ```file_name_reconstruct``` file using ```xxd -revert```
```
python3 remake.py
```

To check the differences between original and reconstructed file, you can use the following command.
```
diff file_name file_name_reconstruct
```

### Encode and S3 Upload
After the ``encode.py`` and ``decode.py`` are hosted on servers like Amazon EC2, run the following command to upload files from Amazon S3
```
python3 encode.py file_name1 file_name2
```

To decode or cache,
```
python3 decode.py file_name1 file_name2
```

### Generate CSVs
To generate CSVs of Download and Upload Requests, run
```
python3 make_csv.py
```


memcached -d -m 2048 -u root -l 127.0.0.1 -p 11211

