import os
import random

path = "parts/myfile_"

remove_parts = random.sample(range(8), 2)
print(remove_parts)

for num in remove_parts:
    os.remove(path+str(num+1))
