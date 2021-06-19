import os
import random

name = "LDC"
# name = "a"
# name = "test"

path = "parts/"+name+"_"

remove_parts = random.sample(range(8), 2)
print(remove_parts)

for num in remove_parts:
    os.remove(path+str(num+1))
