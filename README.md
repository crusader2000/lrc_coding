Repository containing codes w.r.t. MITACS Internship

### Locally Recoverable Codes
This is a coding technique used for Error Correction in Data Centers. It is used in Azure Storage. Ceph, an open source storage system, has plugins which allow using LRC in case of node failures.

### ISAL

### Encoding of Files
The files are first converted to a hexfile using the ```xxd``` command
Use the following command to turn any file into a hexdump
```
python3 main.py
```

```
cmake CMakeLists.txt
make
```

To get back the original file, use the following command. It will produce a ```file_name_reconstruct``` file using ```xxd -revert```
```
python3 remake.py
```

To check the differences between original and reconstructed file, you can use the following command.
```
diff file_name file_name_reconstruct
```

