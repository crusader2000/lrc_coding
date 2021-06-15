import subprocess

file_name = "a.txt"
bashCommand = "xxd -plain " +file_name+" hexdump"
# bashCommand = "xxd " +file_name+" hexdump"

process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
