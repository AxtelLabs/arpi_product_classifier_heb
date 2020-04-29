"""
Program that changes Linux paths into the 
working directory Windows paths
in a python script. And viceversa.

How to run in Linux:

     python3 pathChange.py -d name_of_script_to_change_paths.py

Author: Israel Melendez Montoya
"""

import os
import argparse

# Parses the script name given on the command line
parser = argparse.ArgumentParser(description="changes directories from mac or linux to windows and viceversa")
parser.add_argument('-d','--d', type=str, help='path and name of script to change directories')
parser.add_argument('-i','--i', type=bool, help='invert directory paths back', default=False)

args = vars(parser.parse_args())
script =  args['d']
scriptNew = script
inverse =  args['i']
#opens the script to modify
fin = open(scriptNew, "rt")
#read file contents to string
data = fin.read()
# get the current working directory of the script
#working_directory = os.getcwd()
script = script.split("/")[-1]

script = scriptNew.replace(script,'')
print(script)
#quit()
#data = data.replace(script, "potato")
z = data.find('"')
print(z)
z2 = data.find('"',z+1,z+100)
print(z2)
toreplace = data[z+1:z2]
print(toreplace)
print(script)
#replace all occurrences of the required string
if inverse is False:
    data = data.replace(script, toreplace)
else:
    data = data.replace(toreplace, script)
#close the input file
fin.close()
#open the input file in write mode
fin = open(scriptNew, "wt")
#overrite the input file with the resulting data
fin.write(data)
#close the file
fin.close()