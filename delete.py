import os
import random
import sys
# name = "LDC"
# name = "a"
# name = "test"

files = sys.argv
files.pop(0)
print(files)

for file in files:
    try:
        name,ext = file.split('.')
    except:
        name = file
    print(name)
    path = "parts/"+name+"_"
    
    remove_parts = random.sample(range(8), 2)
    print("GLOBAL - ",remove_parts)
    for num in remove_parts:
            os.remove(path+str(num+1))