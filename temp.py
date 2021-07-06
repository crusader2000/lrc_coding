import subprocess

for i in range(50):
    print("-------------------------%d------------------------"%(i))
    bashCommand = "python3 encode.py"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('UTF-8')
    print(output)

