Repository containing codes w.r.t. MITACS Internship

### Locally Recoverable Codes
This is a coding technique used for Error Correction in Data Centers. It is used in Azure Storage. Ceph, an open source storage system, has plugins which allow using LRC in case of node failures.

### Schifra
An Open Source Error Correcting Library. 
This repository used Reed Solomon Codes for generating global parity blocks.
The local parity blocks are calculated using XOR of individual chunks of each local group
Website : www.schifra.com/

### Encoding of Files
The files are first converted to a hexfile using the ```xxd``` command
Use the following command to turn any file into a hexdump
```
python3 main.py
```

This is followed by encoding using RS Codes. The paramets set are (k,l,r) = (235,20,3)
The C++ file is set to read ```hexdump``` and generate multiple blocks in the ```parts``` directory
```
g++ -o encode encode_file.cpp 
./encode
```

To decode, atleast ``k`` parts must be present in the ```parts``` directory.
This will generate a ```hexdump_reconstruct``` file which is the decoded output.
```
g++ -o decode decode_file.cpp 
./decode
```

To get back the original file, use the following command. It will produce a ```file_name_reconstruct``` file using ```xxd -revert```
```
python3 remake.py
```

To check the differences between original and reconstructed file, you can use the following command.
```
diff file_name file_name_reconstruct
```

