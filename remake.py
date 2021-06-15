import subprocess

file_name = "a.txt"
file_name = file_name.split('.')

bashCommand = "xxd -plain -revert hexdump_reconstruct " +file_name[0]+"_reconstruct."+file_name[1]
# bashCommand = "xxd -r hexdump_reconstruct " +file_name[0]+"_reconstruct."+file_name[1]

process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()