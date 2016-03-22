import sys
import subprocess
import os
import time
from datetime import datetime
 
#timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')

os.chdir("./HealthCheckScripts")
if not os.path.exists("Output"):
    os.makedirs("Output")
if not os.path.exists("temp"):
    os.makedirs("temp")

    
parse = ""



for file in os.listdir("."):
	if ".py" in file and "parse_each_element" in file:
		# print(file)
		parse = file    
    


for file in os.listdir(".\Inputs"):
	file=".\\Inputs\\"+file
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
	print(file)
	print(timestamp)
	
	os.system("python "+parse+" "+file+" "+timestamp)
	# time.sleep(1)
