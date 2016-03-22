import shutil
import os
import glob

#Remove all files from inputs folder and create Inputs Folder again
print(os.curdir)
fname = open("nameOfFile.txt","r")


for line in fname:
	nameOfFile = line
	if os.path.exists('./Inputs'):
		shutil.rmtree('./Inputs')
	if os.path.exists('./statusUpdate.txt'):
		os.remove('./statusUpdate.txt')
	fn = os.path.join(os.path.dirname(__file__), 'Inputs')
	os.makedirs(fn)
	dParser = os.path.abspath(os.curdir) #This is the directory ..\HealthCheckScripts
	print(dParser)
	os.chdir('..')#Moving one folder up


	dASR9k = os.path.abspath(os.curdir) #This is directory till ASR9k. ...\ASR9k
	
	#Creating the logs folder and the outputs folder for that particular day
	if os.path.exists(dASR9k+"\\ParsedLogs\\"+nameOfFile):
		shutil.rmtree(dASR9k+"\\ParsedLogs\\"+nameOfFile)
	
	os.makedirs(dASR9k+"\\ParsedLogs\\"+nameOfFile)
	
	if os.path.exists(dASR9k+"\\ParsedOutputs\\"+nameOfFile):
		shutil.rmtree(dASR9k+"\\ParsedOutputs\\"+nameOfFile)
	
	os.makedirs(dASR9k+"\\ParsedOutputs\\"+nameOfFile)
	
		
	#Adding timestamp
	os.system(dASR9k+'\\directory.py')
	
	# all files in that day's file to Inputs folder in HealthCheckScripts
	fromDirectory = dASR9k + "\\TMO_Outputs\\" + nameOfFile
	toDirectory = dParser+"\\Inputs"
	for txt_file in glob.iglob(fromDirectory+"\\*.*"):
		shutil.copy2(txt_file, toDirectory)
	#Calling health_check.py
	
	os.system(dParser+"\\health_check.py")
	
	
	# copying all logs from script folder to main folder
	fromDirectory = dParser+"\Output"
	toDirectory = dASR9k + "\ParsedLogs\\" + nameOfFile
	source = os.listdir(fromDirectory)
	for files in source:
		if files.startswith("Logs"):
			shutil.move(fromDirectory+"\\"+files,toDirectory)
	
	# #copying all parsed outputs from script folder to main folder
	fromDirectory = dParser+"\\Output"
	toDirectory = dASR9k + "\\ParsedOutputs\\" + nameOfFile
	source = os.listdir(fromDirectory)
	for files in source:
		if files.endswith(".txt"):
			shutil.move(fromDirectory+"\\"+files,toDirectory)

	os.system(dParser+"\\guiDownload.py")
	
	# #deleting inputs folder again
	# shutil.rmtree('./Inputs')
	
	# shutil.rmtree('./statusUpdate.txt')
	