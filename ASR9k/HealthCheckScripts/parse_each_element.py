##########
# Date: 17th Feb 2016
# This file is the main controller for the health-check process.
#########



import sys
import subprocess
import os.path
import re
import time
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict
import json

#######################################################################################################################
 

fname = ""
command_count = 0
pattern = ""
status = ""


statusUpdate = open('statusUpdate.txt','a')
# Global variable to store the starting lines of volage file
tempStartStrVolt = ""

#Global variables needed for admin show environment voltage and table
dictNodeTable = {}
dictHL = {}
dictAttributeTable = {}

dictNodeVolt = {}
dictAttributeVolt = {}

try:
	if(len(sys.argv) != 3):
		print ("steps to run the code:")
		print ("python parse_each_elementv5.py <log_file_without_spaces> <timestamp>")
		sys.exit()

	#This function is to copy the output of show commands of today's files of only those commands which needs to be compared with tomorrow's files
	def copyForHistoric(command_output,cmd_extract):
		# outputFile = open(command_output,"r")
		# outputFile.seek(0)
		nameOfDevice = fname.split('\\')[2]
		dateOfDevice = nameOfDevice.split('_')[1]
		dateOfDevice = dateOfDevice[:-4]
		fileTitle = ""
		historicFolderName = dASR9k+"\\TMO_Outputs\ASR9k_"+dateOfDevice+"\Historic\\"+fname.split('\\')[2].split('-')[0][:-13]
		if not os.path.exists(historicFolderName):
			os.makedirs(historicFolderName)
		#choose the command
		curFile = open(command_output,"r")
		historicFile = open(historicFolderName+"\\"+cmd_extract+".txt","w")
		curFile.seek(0)
				
		for l in curFile:
			historicFile.write(l)
		fout.write('\n\n')
		
	
	#While copying for historic, the name of the text file to be created should also contain the name of the location of that command. This function is for that.		
	def getLocation(command_output):
		fl = open(command_output,"r")
		for line in fl:
			if("show" in line):
				commandArray = line.split(' ')
				return(commandArray[len(commandArray) - 1])


	#################################### COMMAND FUNCTIONS ###########################################
	
	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%Heading Issue%%%%%%%%%%%%%%%%%%%%%%%%%%
	#Same as NCS6k 
	def show_logging_start(command_output):
		parser = open(command_output, 'r')
		
		# temp_list has the known/ non-impacting logs that can be removed.
		temp_file=open('loggingfilequotes.txt','r')
		temp_list=[]
		#fout=open("Output_Log.txt","w")
		#print (temp_list)
		for l in temp_file:
			if(len(l)>1):
				temp_list.append(l.strip())
	  #print (l)
		#print (temp_list)
		temp_file.close()
		##temp_list = ##["%L2-PLIM_ETHER-2-RX_RF","%PKT_INFRA-LINK-3-UPDOWN","%PKT_INFRA-LINEPROTO-5-UPDOWN","%L2-BM-5-MBR_BFD_NOT_RUNNING","%L2-BM-6-ACTIVE","%L2-BFD-6-SESSION_REMOVED",
		##"panini_spio_fill_bdl_mbr_info:"]
		
		
		flag = 0
		for curline in parser:
			for f in temp_list:
				if f in curline:
					flag = 1
			if flag == 0:
				fout.write(curline)
			else:	
				flag = 0
		fout.write("\n")
		
	#Madhukar for admin show environment temperature
	def admin_temperature(command_output):
	
		def checkWithThreshold(data,threshold):
			parsedData = ""
			for line in data.splitlines():
				lineArray = line.split("\t")
				tempValue = float(lineArray[len(lineArray)-1])
				if(tempValue>threshold):
					parsedData = parsedData + line +"\n"
			return parsedData	
			

		outputFile = open(command_output,"r")
		outputFile.seek(0)
		toBeprinted = ""
		allLines = outputFile.readlines()

		threshold_FC = 80.00
		threshold_FT = 80.00
		threshold_RP = 80.00
		threshold_LC = 95.00
		for line in allLines:
			if(line.isspace()):
				allLines.remove(line)
		lineNumber = 0
		title = ""

		while not("GMT" in allLines[lineNumber] or "PST" in allLines[lineNumber]):
			fout.write(allLines[lineNumber])
			lineNumber = lineNumber+1
		fout.write(allLines[lineNumber])
		heading = allLines[lineNumber+1]
		lineNumber = lineNumber + 2

		while(lineNumber<len(allLines)):
			if("0/" in allLines[lineNumber] and lineNumber>0):
				if("/FC" in allLines[lineNumber]):
					data = ""
					title = allLines[lineNumber]
					lineNumber = lineNumber+1
					while("host" in allLines[lineNumber]):
						data = data + allLines[lineNumber]
						lineNumber = lineNumber+1
					lineNumber = lineNumber - 1
					parsedData = checkWithThreshold(data,threshold_FC)
					if (parsedData):
						toBeprinted = toBeprinted + title + parsedData

				elif("/FT" in allLines[lineNumber]):
					data = ""
					title = allLines[lineNumber]
					lineNumber = lineNumber+1
					while("host" in allLines[lineNumber]):
						data = data + allLines[lineNumber]
						lineNumber = lineNumber+1
					lineNumber = lineNumber - 1
					parsedData = checkWithThreshold(data,threshold_FT)
					if (parsedData):
						toBeprinted = toBeprinted + title + parsedData

					
				elif("/RP" in allLines[lineNumber]):
					data = ""
					title = allLines[lineNumber]
					lineNumber = lineNumber+1
					while("host" in allLines[lineNumber]):
						data = data + allLines[lineNumber]
						lineNumber = lineNumber+1
					lineNumber = lineNumber - 1
					parsedData = checkWithThreshold(data,threshold_RP)
					if (parsedData):
						toBeprinted = toBeprinted + title + parsedData

					
				else:
					data = ""
					title = allLines[lineNumber]
					lineNumber = lineNumber+1
					while("host" in allLines[lineNumber]):
						data = data + allLines[lineNumber]
						lineNumber = lineNumber+1
					lineNumber = lineNumber - 1
					parsedData = checkWithThreshold(data,threshold_LC)
					if (parsedData):
						toBeprinted = toBeprinted + title + parsedData
			
			lineNumber = lineNumber + 1
				
		if(toBeprinted):
			fout.write(heading+toBeprinted)
		fout.write("\n")
			
	
	#Madhukar for admin show platform
	def admin_show_platform(command_output):
		outputFile = open(command_output,"r")
		outputFile.seek(0)
		toBePrinted = ""
		heading = ""
		flag = 0
		for line in outputFile:
			if(line[0].isnumeric()):
				if ("IOS XR RUN" in line) or ("READY" in line) or ("OK" in line):
					continue
				else:
					toBePrinted = toBePrinted + line
					flag = 1
			elif("Node" in line or "-------------" in line):
				heading = heading + line
				continue
			if(flag == 0):
				fout.write(line)

		if(flag == 1):
			fout.write(heading+toBePrinted)
				
		fout.write("\n")
	

	#Madhukar show cef platform oor location
	def show_cef_platform(command_output):
		outputFile = open(command_output,"r")
		outputFile.seek(0)
		fl_object = 0 #This is to print all lines above object
		threshold = 0.85
		
		toBePrinted = ""

		for line in outputFile:
			if("pd_oor_info" in line):
				break
				
			if("OBJECT" in line):
				fl_object  = 1
				toBePrinted = toBePrinted + line
				

			if(fl_object == 0):
				fout.write(line)
			elif not("OBJECT" in line):
				if(line != "\n"):
					line1 = line.split()
					
					#Finding the current and maximum pdUsage and Prm usage by converting into integers 
					pdUsage = line1[1]
					pdUsage1 = pdUsage.split('(')
					cur_pdUsage = pdUsage1[0]
					max_pdUsage = pdUsage1[1]
					max_pdUsage = max_pdUsage[:-1] # This is to remove the last )
					cur_pdUsage = int(cur_pdUsage)
					max_pdUsage = int(max_pdUsage)
					
					prmUsage = line1[2]
					prmUsage1 = prmUsage.split('(')
					cur_prmUsage = prmUsage1[0]
					max_prmUsage = prmUsage1[1]
					max_prmUsage = max_prmUsage[:-1] # This is to remove the last )
					cur_prmUsage = int(cur_prmUsage)
					max_prmUsage = int(max_prmUsage)
					
					
					if( (threshold * max_pdUsage <= cur_pdUsage) or (threshold*max_prmUsage <= cur_prmUsage) ):
						toBePrinted = toBePrinted + line
					
		if(toBePrinted.count("\n") > 7 ):
			fout.write(toBePrinted)
		outputFile.close()
		fout.write('\n\n')
		

	#Madhukar for show controllers np soft-errors all all
	def show_controllers(command_output):
		outputFile = open(command_output,"r")
		outputFile.seek(0)
		toBeprinted = ""
		allLines = outputFile.readlines()
		i = 0
		outputFile.seek(0)
		for line in outputFile:
			if("Blk" in line):
				line_counter = i
				break
			i = i+1
		outputFile.seek(0)
		toBeprinted = toBeprinted + allLines[line_counter] + allLines[line_counter+1]
		for line in outputFile:
			length = len(line)
			curLine2 = line
			curLine2 = curLine2.replace(" ","")
			length2 = len(curLine2)
			if (curLine2[0].isnumeric()):
				if((curLine2[length2-2] != "0") or (curLine2[length2-3] != "0") or (curLine2[length2-4] != "0") or (curLine2[length2-5] != "0") or (curLine2[length2-6] != "0")):
					toBeprinted = toBeprinted + line
			elif not("-- " in line or "Blk" in line or line.isspace()):
				fout.write(line)
		fout.write(toBeprinted)
		outputFile.close	
		fout.write('\n\n')
		

	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Heading issue%%%%%%%%%%%%%%%%%%%%%%%%%
	#Madhukar admin show reboot-history
	def show_reboot(command_output,prevFileLocation):
		outputFileToday = open(command_output,"r")
		outputFileYest = open(prevFileLocation,"r")

		outputFileToday.seek(0)

		#Creating all the lines having Cause: in them from yesterday file to check that with today's file
		checkString = []
		allLines = outputFileToday.readlines()

		outputFileToday.seek(0)
		toBePrinted = ""

		for line_yest in outputFileYest:
			if("Cause:" in line_yest):
				checkString.append(line_yest[4:( len(line_yest) )]) #This is done to remove the \n and sl no from the Cause:line

		flag = 1
		for line in outputFileToday:
			# flag = 1
			if("Cause:" in line):
				flag = 0
				if not(line[4:( len(line) )] in checkString): #Same funda as the previous comment
					flag = 1
			if (flag == 1):
				toBePrinted = toBePrinted + line
				
		if(toBePrinted.count("\n") > 7 ):
			fout.write(toBePrinted)
		else:
			for line in allLines:
				if not("GMT" in line or "PST" in line):
					fout.write(line)
				else:
					break
			fout.write(line)
		fout.write('\n\n')
		

	#Madhukar show asic-errors all location
	def show_asic(command_output,prevFileLocation):
		def getLineNumbers(f):
			lineCounter = 0	
			fia_line = -1
			pcie_line = -1
			prm_line = -1
			for line in f:
				if "Fia ASIC Error Summary" in line:
					fia_line = lineCounter
				elif "Pcie ASIC Error Summary" in line:
					pcie_line = lineCounter
				elif "Prm_np ASIC Error Summary" in line:
					prm_line = lineCounter
				lineCounter = lineCounter + 1
			return(fia_line,pcie_line,prm_line,lineCounter)

		#Function to seperate if we need to get count title and count
		def splitToGetCount(line):
			line1 = line.split(':')
			title = line1[0]
			cnt = line1[1]
			return(title,int(cnt))
			
		def createList(start,end,fl):
			fl.seek(0)
			lineNumber = 0
			summa = {}
			dict = []
			orderOfList = []
			flag = 0
			k=0
			# This for is to move the pointer to first instance in of summary
			for i in range(0,start+1):
				next(fl)
			lineNumber = start+2
			
			for line in fl:
				if(lineNumber < end):
					if "Instance" in line:
						i = 0
						# print(line)
						for i in range(0,8):
							# print(line)
							title,cnt = splitToGetCount(line)
							# print(title,cnt)
							summa.update({title : cnt})
							if (flag == 0):
								orderOfList.append(title)
							# print(summa)
							line = fl.readline()
							i = i+1
						# print("&&&&&&&&&&&&&&&&&&&&&&&PRINTING EACH DICTIONARY CREATED&&&&&&&&&&&&&&&&&&")
						# print(summa)
						dict.append(summa)
						flag = 1
						# print("%%%%%%%%%%%%%%%%%%PRINTING DICT%%%%%%%%%%%%%%%%%%%%%%")
						# print(dict)
						summa = {}
						
					lineNumber = lineNumber + 9
					
				else:
					break
			# print(dict)
			return dict,orderOfList

		
		outputFileToday = open(command_output,"r")
		outputFileYest = open(prevFileLocation,"r")



		outputFileToday.seek(0)
		outputFileYest.seek(0)

		orderOfList = []

		#getting the line numbers of the different sections where fia pcie and prm is written in today's file.
		fia_line_cur, pcie_line_cur, prm_line_cur, lastLine_cur = getLineNumbers(outputFileToday) 
		outputFileToday.seek(0)

		fia_line_yest, pcie_line_yest, prm_line_yest, lastLine_yest = getLineNumbers(outputFileYest) 
		outputFileYest.seek(0)
		fia_string = ""
		prm_string = ""
		pcie_string = ""

		#writing this to output file
		outputFileToday.seek(0)

		i = 0

		#This is to print only the command
		for i in range(0,2):
			line = outputFileToday.readline()
			fout.write(line)
			i = i+1

		if(fia_line_cur != -1):
			#creating a list of dictionaries where every instance values is a dictionaries
			fia_list_today = []
			fia_list_yest = []
			fia_list_today,orderOfList = createList(fia_line_cur,pcie_line_cur,outputFileToday)
			fia_list_yest,orderOfList = createList(fia_line_yest,pcie_line_yest,outputFileYest)
			
			#preparing a string with delta values
			diff = {}
			
			# temp_fia_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent fia_string to output to file
			i = 0
			fl_fia = 0 #Flag value to check if there are any new entries only then print
			for i in range(0,len(fia_list_today)):

				diff = {key: fia_list_today[i][key]-fia_list_yest[i][key] for key in fia_list_today[i] if key in fia_list_yest[i]} #This is used to find the difference
				for s in orderOfList:
					fl_fia= 0
					if("Instance" in s):
						temp_fia_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent fia_string to output to file
						temp_fia_string = temp_fia_string +"-------------------------------------" + "\n" +   s + ":" + str(fia_list_today[i][s]) +  "\n"
					elif(str(diff[s]) != "0"):
						fl_fia =1
						temp_fia_string = temp_fia_string  +  s + ":" + str(fia_list_today[i][s]) + "  -  " + str(diff[s]) + "\n"
					if(fl_fia == 1):
						fia_string = fia_string + temp_fia_string
				i = i+1
			outputFileToday.seek(0)
			#consolidating fia titles in the fia_string to be written
			lines = outputFileToday.readlines()
			fia_string = lines[fia_line_cur - 1] + lines[fia_line_cur] + lines[fia_line_cur + 1] +fia_string
			fout.write(fia_string)
			
				
		if(pcie_line_cur != -1):
			#creating a list of dictionaries where every instance values is a dictionaries
			pcie_list_today = []
			pcie_list_yest = []
			pcie_list_today,orderOfList = createList(pcie_line_cur,pcie_line_cur,outputFileToday)
			pcie_list_yest,orderOfList = createList(pcie_line_yest,pcie_line_yest,outputFileYest)
			
			#preparing a string with delta values
			diff = {}
			
			# temp_pcie_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent pcie_string to output to file
			i = 0
			fl_pcie = 0 #Flag value to check if there are any new entries only then print
			for i in range(0,len(pcie_list_today)):

				diff = {key: pcie_list_today[i][key]-pcie_list_yest[i][key] for key in pcie_list_today[i] if key in pcie_list_yest[i]} #This is used to find the difference
				for s in orderOfList:
					fl_pcie= 0
					if("Instance" in s):
						temp_pcie_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent pcie_string to output to file
						temp_pcie_string = temp_pcie_string +"-------------------------------------" + "\n" +   s + ":" + str(pcie_list_today[i][s]) +  "\n"
					elif(str(diff[s]) != "0"):
						fl_pcie =1
						temp_pcie_string = temp_pcie_string  +  s + ":" + str(pcie_list_today[i][s]) + "  -  " + str(diff[s]) + "\n"
					if(fl_pcie == 1):
						pcie_string = pcie_string + temp_pcie_string
				i = i+1
			#consolidating fia titles in the fia_string to be written
			outputFileToday.seek(0)
			lines = outputFileToday.readlines()
			pcie_string = lines[pcie_line_cur - 1] + lines[pcie_line_cur] + lines[pcie_line_cur + 1] +pcie_string
			fout.write(pcie_string)
			
				
		if(prm_line_cur != -1):
			#creating a list of dictionaries where every instance values is a dictionaries
			prm_list_today = []
			prm_list_yest = []
			prm_list_today,orderOfList = createList(prm_line_cur,prm_line_cur,outputFileToday)
			prm_list_yest,orderOfList = createList(prm_line_yest,prm_line_yest,outputFileYest)
			
			#preparing a string with delta values
			diff = {}
			
			# temp_prm_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent prm_string to output to file
			i = 0
			fl_prm = 0 #Flag value to check if there are any new entries only then print
			for i in range(0,len(prm_list_today)):

				diff = {key: prm_list_today[i][key]-prm_list_yest[i][key] for key in prm_list_today[i] if key in prm_list_yest[i]} #This is used to find the difference
				for s in orderOfList:
					fl_prm= 0
					if("Instance" in s):
						temp_prm_string = "" #This string is temporariliy storing all the difference values. If there is a change then only printing to permanent prm_string to output to file
						temp_prm_string = temp_prm_string +"-------------------------------------" + "\n" +   s + ":" + str(prm_list_today[i][s]) +  "\n"
					elif(str(diff[s]) != "0"):
						fl_prm =1
						temp_prm_string = temp_prm_string  +  s + ":" + str(prm_list_today[i][s]) + "  -  " + str(diff[s]) + "\n"
					if(fl_prm == 1):
						prm_string = prm_string + temp_prm_string
				i = i+1
			outputFileToday.seek(0)
			lines = outputFileToday.readlines()
			prm_string = lines[prm_line_cur - 1] + lines[prm_line_cur] + lines[prm_line_cur + 1] +prm_string
			fout.write(prm_string)
		fout.write('\n\n')


	#Madhukar for show processes memory detail
	def show_processes_memory(command_output):
		outputFile = open(command_output,"r")
		outputFile.seek(0)
		fl_jid = 0 #This is to print all lines above jid
		threshold = 0.8
		heading = ""

		for line in outputFile:
			if("JID" in line):
				fl_jid  = 1
				heading = heading + line
				
			if(fl_jid == 0):
				if("------" in line):
					heading = heading + line
				else:
					fout.write(line)
				
			elif not("JID" in line):
				if not("------" in line or "Total" in line or "data" in line or "stack" in line or "malloced" in line or "INFINITY" in line):
					line1 = line.split()
					
					#Finding the current and maximum pdUsage and Prm usage by converting into integers 
					#Finding the current and maximum pdUsage and Prm usage by converting into integers 
					dynamic = line1[4]
					
					
					dynamic_max = line1[5]
					
					if(len(dynamic)>1):
						size = ""
						size = dynamic[len(dynamic) - 1]
						dynamic = dynamic[:-1] # This is to remove the last M or K
					dynamic = int(dynamic)
					if(size == "M"):
						dynamic = dynamic * 1024
					
					# print(dynamic)
					if(len(dynamic_max)>1):
						size = ""
						size = dynamic_max[len(dynamic_max) - 1]
						dynamic_max = dynamic_max[:-1] # This is to remove the last M or K
					dynamic_max = int(dynamic_max)
					if(size == "M"):
						dynamic_max = dynamic_max * 1024
						
					if(dynamic >= dynamic_max):
						fout.write(line)
			
		fout.write('\n\n')

		
	#Madhukar show l2vpn bridge-domain summary
	def show_l2vpn_bridge(command_output,prevFileLocation):
		# def createDict(file_handler):
		def createDictionaries(array):
			dictionary = {}
			for s in array:
				s_arr = s.split(":")
				s_arr = [item.strip() for item in s_arr]
				dictionary.update({s_arr[0] : s_arr[1]})
			return array,dictionary

		
		outputFileToday = open(command_output,"r")
		outputFileYest = open(prevFileLocation,"r")
		
		
		allLines = outputFileToday.readlines()

		#This is to bring the command and time stamp on same line
		j = 0

		for i in range(0,5):
			if allLines[j].isspace():
				allLines.pop(j)
			j = j+1
		allLines[0] = allLines[0][:-1]+allLines[1]
		allLines.pop(1)
		#This is done to combine since programmed of Partially Programmed for Number of groups is coming on next line
		allLines[2] = allLines[2][:-1] + allLines[3]
		allLines.pop(3)

		#Done as this line does not have a comma. Random formats of O/P
		temp = []
		temp = allLines[4].split(" ")
		allLines[4] = "Number of ACs: " + temp[3] + ", " + temp[4] +" " + temp[5] +" " + temp[6] +" " + temp[7] +" " + temp[8] +" " + temp[9][:-1]
		temp = []
		temp = allLines[5].split(" ")
		allLines[5] = "Number of PWs: " + temp[3] + ", " + temp[4] + temp[5] +" " + temp[6] +" " + temp[7] +" " + temp[8] +" " + temp[9]+" " + temp[10] +" " + temp[11][:-1]

		listOfDictionaries_today = []

		forPrintArray_today = []

		for i in range(2,8):
			array = allLines[i].split(',')
			array_return , dictionary = createDictionaries(array)
			listOfDictionaries_today.append(dictionary)
			forPrintArray_today.append(array_return)
		# print(forPrintArray_today[0])	


		#Same for yesterday's file
		allLines_yest = outputFileYest.readlines()

		j = 0

		for i in range(0,5):
			if allLines_yest[j].isspace():
				allLines_yest.pop(j)
			j = j+1
		allLines_yest[0] = allLines_yest[0][:-1]+allLines_yest[1]
		allLines_yest.pop(1)


		#This is done to combine since programmed of Partially Programmed for Number of groups is coming on next line
		allLines_yest[2] = allLines_yest[2][:-1] + allLines_yest[3]
		allLines_yest.pop(3)
		#Done as this line does not have a comma. Random formats of O/P
		temp = []
		temp = allLines_yest[4].split(" ")

		allLines_yest[4] = "Number of ACs: " + temp[3] + ", " + temp[4] +" " + temp[5] +" " + temp[6] +" " + temp[7] +" " + temp[8] +" " + temp[9][:-1]
		temp = []
		temp = allLines_yest[5].split(" ")
		allLines_yest[5] = "Number of PWs: " + temp[3] + ", " + temp[4] + temp[5] +" " + temp[6] +" " + temp[7] +" " + temp[8] +" " + temp[9]+" " + temp[10] + " " + temp[11][:-1]

		listOfDictionaries_yest = []

		for i in range(2,8):
			array_yest = allLines_yest[i].split(',')
			array_return_yest,dictionary_yest = createDictionaries(array_yest)
			listOfDictionaries_yest.append(dictionary_yest)

		j = 0
		fout.write(allLines[0]+allLines[1])
		for i in range(0,len(listOfDictionaries_today)):
			toBePrinted = ""
			array_elements = ""
			diff = {key: int(listOfDictionaries_today[i][key])-int(listOfDictionaries_yest[i][key]) for key in listOfDictionaries_today[i] if key in listOfDictionaries_yest[i]} #This is used to find the difference
			flag = 0
			for key,value in diff.items():
				# print(key,value)
				if(value != 0):
					toBePrinted = toBePrinted + str(key)+ str(value) + "|"
					flag = 1
			if(flag == 1):
				for val in forPrintArray_today[j]:
					array_elements = array_elements + val
				(array_elements + "    |" +toBePrinted).replace("\n","")
				fout.write("\n"+array_elements + "    |" +toBePrinted)
			j = j+1
		fout.write("\n")


	#Madhukar show prm server tcam summary all all all location
	def show_prm_server(command_output):
		outputFile = open(command_output,"r")
		allLines = outputFile.readlines()
		fout.write(allLines[0] + allLines[1] + allLines[2] + allLines[3] + allLines[4])
		fout.write("OUTPUT SKIPPED\n")
		fout.write("\n")


	#Saip show admin environment leds
	def admin_leds(command_output):
		f=open(command_output,"r")
		
		s=""
		s1=""
		head=""
		head1=""

		line=f.readline()
		print(line)
		while not("PST" in line or "GMT" in line):
			# print(line)
			head+=line
			line=f.readline()
		head1=head.replace("\n","")
		fout.write(head1)
		fout.write('\n')
		fout.write(line)
			

		line=f.readline()

		while(line.find("RP")==-1):
				s1+=line
				line=f.readline()

		while (len(line.split())!=0):
			if("RP" in line):
				s+=line
				line=f.readline()
			if ("Off" in line):
				line=f.readline()
			else:
				#print(line)
				s+=line
				line=f.readline()
				
		if len(s) > 16 :
			fout.write(s1)
			fout.write(s)
			fout.write("---------------------------------------------")
		fout.write("\n")

	#Saip show health sys db
	def sysdb(command_output):
		print("Inside Function")
		f = open(command_output, "r")
		line = f.readline()
		s=""
		head=""
		head1=""

		while not ("PST" in line or "GMT" in line):
			head+=line
			line=f.readline()

		print("Outside while 1")
		head1=head.replace('\n','')
		fout.write(head1)
		fout.write('\n')
		fout.write(line)

		while line:
			if(line.find("sysdb health")!=-1):
				if(line.find("health OK")!=-1):
					s=""
					line=f.readline()
				else:
					s=s+line
					fout.write(s)
					line=f.readline()
					if("health check finished" in line):
						break
			line=f.readline()
	
		fout.write("\n")

	#SaiP show health gsp 
	def show_gsp(command_output):
		f = open(command_output, "r")

		s=""
		f.seek(0)
		line = f.readline()
		head=""
		head1=""

		while not ("PST" in line or "GMT" in line):
			head+=line
			line=f.readline()

		head1=head.replace('\n','')
		fout.write(head1)
		fout.write('\n')
		fout.write(line)
			

		while line:
			#print(line)
			if(line.find("Summary: gsp is healthy")==-1):
				s=s+line
				line=f.readline()
			else:
				s=""
				line=f.readline()
		
		fout.write("\n")


	#SaiP show hw-module fpd location all
	def show_hw_module(command_output):
		f = open(command_output,'r')
		flag=0
		head=""
		temp1=""
		temp2=""
		line= f.readline()

		head1=""
		head2=""


		while not ("PST" in line or "GMT" in line):
			head1+=line
			line=f.readline()

		head2=head1.replace('\n','')
		fout.write(head2)
		fout.write('\n')
		fout.write(line)

		for i in range(7):
			line=f.readline()
			head=head+line

		while line :
			temp1+=line
			if(line.find('Yes')!=-1):
				flag = 1
			line=f.readline()	
			if(line.find('----------')!=-1):
				if(flag==1):
					temp2+=temp1
					temp1=""
					flag=0
					
					
				else:
					temp1=""
		fout.write(head)
		fout.write(temp2)	
		fout.write("\n")

	#SaiP show l2vpn forwarding resource detail location
	def show_l2vpn_forwarding(command_output):
		f = open(command_output, "r")
		line = f.readline()
		head=""
		head1=""

		while not ("PST" in line or "GMT" in line):
			head+=line
			line=f.readline()

		head1=head.replace('\n','')
		fout.write(head1)
		fout.write('\n')
		fout.write(line)
		line=f.readline()

		while line:
			if (line.find('GREEN')== -1):
				if not ("shared memory resource:" in line):
					fout.write(line)	
			line=f.readline()
		fout.write("\n")


	#SaiP show memory summary location all
	def show_memory(command_output):
		rp_threshold = 25
		lc_threshold = 20
		f = open(command_output,'r')
		f.seek(0)
		line=f.readline()
		s= ""
		flag=0
		#Writes the first two lines (command and the time)
		head=""
		head1=""

		#print(line)
		while not ("PST" in line or "GMT" in line):
			head+=line
			line=f.readline()

		head1=head.replace('\n','')
		fout.write(head1)
		fout.write('\n')
		fout.write(line)
		line=f.readline()
		while line :
			
			if("RP" in line):
				if("node" in line):
					str1=line
					flag=1
				
			else:
				if("node" in line):	
					flag=0
					str2=line
			line=f.readline()
			#Threshold calculation 20% for LC & 25% for RP
			if ("Application" in line):
				l1 = line.split()
				l2= l1[3].split('M')
				l3= l1[4].split('(')
				l4=l3[1].split('M')
				available_mem = int(l4[0])
				total_mem = int(l2[0])
				res_mem= (available_mem/total_mem)*100
				# rounding off to two decimal places
				per_mem =format(res_mem, '.2f')
				if(flag ==1):
					if ( float(per_mem) <= rp_threshold):
						fout.write("------------------------------------------------------------------")
						fout.write("\n")
						fout.write(str1)
						fout.write("------------------------------------------------------------------")
						fout.write("\n")
						fout.write("Application Memory" + " :   " +str(per_mem) + "%")
						fout.write("\n")
						fout.write("\n")
						line=f.readline()
						flag=0
						s=""
				else :
					if ( float(per_mem) <= lc_threshold):
						fout.write("------------------------------------------------------------------")
						fout.write("\n")
						fout.write(str2)
						#f1.write("\n")
						fout.write("------------------------------------------------------------------")
						fout.write("\n")
						fout.write("Application Memory" + " :   " +str(per_mem) + "%")
						fout.write("\n")
						fout.write("\n")
						line=f.readline()
						flag=0
		fout.write("\n")

	#SaiP show pfm location all	
	def show_pfm(input_today,input_prev):
		#making a list of unique values foy yesterday's outputs
		def checkPrev(f1,checkList_prev,l):
			node_prev=""
			while l :
				if("node" in l):
					node_prev=l
				l=f1.readline()
				if("Raised Time" in l):
					l=f1.readline()
					if("---------" in l):
						l=f1.readline()
						while l :
							s1=l.split("|")
							if(s1[0]=="Mon Jan 01 00:00:000"):
								l=f1.readline()
							else:
								checkList_prev.append(s1[0])
								l=f1.readline()
								if (len(l.strip()) == 0) :
									return 
										
				l=f1.readline()

			
		#making a list of unique values foy today's outputs		
		def checkToday(f,checkList_today,line):
			node_today=""
			while line :
				if("node" in line):
					node_today=line
				line=f.readline()			
				if("Raised Time" in line):
					line=f.readline()
					if("---------" in line):
						line=f.readline()
						while line :
							s0=line.split("|")
							if(s0[0]=="Mon Jan 01 00:00:000"):
								line=f.readline()
							else:
								checkList_today.append(s0[0])
								line=f.readline()
								if (len(line.strip()) == 0) :
									return node_today		
				line=f.readline()
			

		#for comparing two days outputs
		def compare(f,f1,checkList_prev,checkList_today):
			result=set(checkList_today)-set(checkList_prev)
			list1=list(result)
			len_result=len(list1)
			to_write=""
			if not result:
				return
			else:
				f.seek(0)
				line=f.readline()
				for i in range(len_result):
					f.seek(0)
					line=f.readline()
					while line :
						if (list1[i] in line):
							to_write+=line
							line=f.readline()
						else:
							line=f.readline()
					
			return to_write
		#Writing result in outputfile
		def finalOutput(f,fout,to_write,node_prev_name):
			head=""
			f.seek(0)
			line=f.readline()
			if(to_write):
				while line:
					if(line==node_prev_name):
						for i in range(6):
							head+=line
							line=f.readline()
					else:
						line=f.readline()
					
				line=f.readline
				fout.write(head)
				fout.write("--------------------+--+-----------------+---+-------+--------------+----------")
				fout.write("\n")
				
				fout.write(to_write)
				fout.write("\n")
				fout.write("\n")

		f= open(input_today,"r")
		f1=open(input_prev,"r")
		count_node_prev=0
		name=""
		count_node_today=0
		str1=""
		head_wo=""
		result=""
		for line in f.readlines():
			if 'node' in line:
				count_node_today+=1
		for l in f1.readlines():
			if 'node' in l:
				count_node_prev+=1
				
		checkList_prev=[]
		checkList_today=[]
		line=f.readline()
		l=f1.readline()
		node_prev_name=""
		node_today_name=""
		to_writefile=""
		list_node_PosToday=[]
		list_node_PosPrev=[]
		count_lines_prev=0
		count_lines_today=0
		str_prev=""
		str_today=""
		
		f.seek(0)
		f1.seek(0)
		line=f.readline()
		#Printing command till GMT
		head1=""
		head2=""

		while not ("PST" in line or "GMT" in line):
			head1+=line
			line=f.readline()

		head2=head1.replace('\n','')
		fout.write(head2)
		fout.write('\n')
		fout.write(line)	
		phrase='node'
		# position of nodes in today's file
		with open(input_today) as f:
				for i, l2 in enumerate(f, 1):
					if phrase in l2:
						list_node_PosToday.append(i)
					
		# position of nodes in yesterday's file
		with open(input_prev) as f1:
				for i, l3 in enumerate(f1, 1):
					if phrase in l3:
						list_node_PosPrev.append(i)
						
		
		f1=open(input_prev,"r")
		f= open(input_today,"r")
		f1.seek(0)
		f.seek(0)
		line=f.readline()
		l=f1.readline()
		while line :
			if "node" in line :
				str_today+=line
			line=f.readline()
		while l :
			if "node" in l :
				str_prev+=l
			l=f1.readline()
		#if node_prev not equal to node_today
		nameOfDevice = fname.split('\\')[2]
		dateOfDevice = nameOfDevice.split('_')[1]
		dateOfDevice = dateOfDevice[:-4]
		date_today_format=datetime.strptime(dateOfDevice, '%m%d%Y')
		date_prev=date_today_format-timedelta(days=1)
		final_date_today1=date_today_format.strftime('%b  %d').lstrip("0").replace(" 0"," ")
		final_date_today2=date_today_format.strftime('%b %d').lstrip("0").replace(" 0"," ")
		final_date_prev1=date_prev.strftime('%b  %d').lstrip("0").replace(" 0"," ")
		final_date_prev2=date_prev.strftime('%b %d').lstrip("0").replace(" 0"," ")
		
		
		f.seek(0)
		f1.seek(0)
			
		#Global variables for storing data
	#for calling the functions number of node times
		if(count_node_today==count_node_prev)and (str_prev==str_today):
			for i in range(count_node_today):
				f.seek(0)
				f1.seek(0)
				for j in range(list_node_PosToday[i]):
					line=f.readline()
				for k in range(list_node_PosPrev[i]):
					l=f1.readline()
				checkList_today=[]
				checkList_prev=[]
				node_today_name = checkToday(f,checkList_today,line)
				node_prev_name=checkPrev(f1,checkList_prev,l)
				to_write=compare(f,f1, checkList_prev, checkList_today)
				finalOutput(f,fout,to_write, l)
		else:
			while(line.find("node")==-1):
				line=f.readline()
			while line :
				if "node" in line:
					for i in range(7):
						head_wo+=line
						line=f.readline()
						
					while(len(line.strip()) != 0):
						str1=line.split("|")
						if(str(final_date_prev1)in str1[0]) or (str(final_date_today1)in str1[0]) or (str(final_date_prev2)in str1[0]) or (str(final_date_today2)in str1[0]):
							result+=line
							line=f.readline()
						else:	
							line=f.readline()
					if result:   
						fout.write(head_wo)
						fout.write(result)
						fout.write("\n")
						result=""
						head_wo=""
					else:
						head_wo=""
				else:
					line=f.readline()
		
	
	
	#Saip show lpts pifib hardware police location <>
	def show_lpts(todaysFile, prevDayFile):
		def readFile(fileName):
			readFile = open(fileName, "r")
			readLines = readFile.readlines()
			location_count = 0
			location_list = [[]]
			location = []
			final_location_list = dict()
			line=readFile.readline()

			for i, item in enumerate(readLines):
				if not(("RP" in item) or ("GMT" in item) or ("PST" in item) or ("show" in item)or (len(item.split())==0)):
					location_list[location_count].append(item)
				if item.find('Node') != -1:
					location.append(item.split()[1].split(":")[0])
					for i in range(1,5):
						stat = location_list[location_count - 1].pop()
						location_list[location_count].insert(0, stat)
			for i in range(len(location)):
				final_location_list[location[i]] = location_list[i]
			return final_location_list, location

		def parse_dicts(todayDict, prevdayDict, todayslocation, prevDaylocation):

			tem_content = []
			for item in todayslocation:
				todayDict[item][5]=todayDict[item][5].replace("Dropped","Dropped             Delta")
				for value in range(0, 5):
					tem_content.append(todayDict[item][value])
				#print(tem_content)
				tem_content.append(todayDict[item][5])
				tem_content.append("-----------------------------------------------------------------------------------------------------------------------------------------\n")
				#print(len(tem_content))
				#print(todayDict[item][7])
				tem_len = len(todayDict[item])-7
				for value in range(7, tem_len):
					split_var_today = todayDict[item][value].split()
					split_var_prevday = prevdayDict[item][value].split()
					try:

						if int(split_var_today[6]) - int(split_var_prevday[6]) > 0:
							col2_attr = str(int(split_var_today[6]) - int(split_var_prevday[6]))
							todayDict[item][value] = todayDict[item][value].replace(split_var_today[7], (col2_attr)+"                 "+split_var_today[7])
							tem_content.append(todayDict[item][value])

						elif int(split_var_today[6]) - int(split_var_prevday[6]) < 0:
							col2_attr = str(int(split_var_today[6]) - int(split_var_prevday[6]))
							todayDict[item][value] = todayDict[item][value].replace(split_var_today[7], (col2_attr)+"                 "+split_var_today[7])
							tem_content.append(todayDict[item][value])
						else:
							col2_attr=0
					except IndexError as ie:
						print("Error")
			return tem_content
			
		f=open(todaysFile,'r')
		line=f.readline()
		final_output= []
		head=[]
		head_final=""
		todaysFileDict, todayslocation = readFile(todaysFile)
		prevDayFileDict, prevDaylocation = readFile(prevDayFile)
		#print("hello")
		final_output= parse_dicts(todaysFileDict, prevDayFileDict, todayslocation, prevDaylocation)


		if (len(final_output)>7 ):
			while not ("PST" in line or "GMT" in line):
				if(len(line.split())!=0):
					#print(line)
					head.append(line.rstrip('\n'))
					line=f.readline()
				else :
					line=f.readline()
			head_final=''.join(head)
			fout.write(head_final)
			fout.write('\n')
			fout.write(line)
			for sub_item in final_output:
				fout.write(sub_item)
			fout.write("\n")
			fout.write("------------------------\n")
		else :
			while not ("PST" in line or "GMT" in line):
				if(len(line.split())!=0):
					#print(line)
					head.append(line.rstrip('\n'))
					line=f.readline()
				else :
					line=f.readline()
			head_final=''.join(head)
			fout.write(head_final)
			fout.write('\n')
			fout.write(line)
		fout.write("\n")


	#Saip show redundancy
	def show_redundancy(command_output):
	
		def check_ready_printlines(f,fout,line):

			str=""
			s=""
			l3=""
			line=f.readline()
			for i in range(2):
				s+=line
				line=f.readline()

			while (len(line.strip())!=0):
				if ("  Ready" in line):
					line=f.readline()
				else:
					str+=line
					line=f.readline()

			for i in range(5):
				line=f.readline()
				l3+=line
			if str:
				fout.write(s)
				fout.write(str)
			fout.write("\n")
			fout.write(l3)
			return
			
			
		def check_nodeStatus(inputFile):
			f=open(inputFile,"r")
						
			s1=""
			s2=""
			s3=""

			line=f.readline()
			head=""
			head1=""
			
			while not ("PST" in line or "GMT" in line):
				head+=line
				line=f.readline()

			head1=head.replace('\n','')
			fout.write(head1)
			fout.write('\n')
			fout.write(line)
			line=f.readline()
			while (line.find("Standby node")==-1):
				s2+=line
				line=f.readline()
			
			while (line.find("PRIMARY")==-1):
				if ("is NSR-ready" in line) or ("is ready" in line) :
					line=f.readline()
						
				else:
					s1+=line
					line=f.readline()
			while (len(line.split())!=0):
				s3+=line
				line=f.readline()
				
			
			if s1:
				fout.write(s2)
				fout.write(s1)
				fout.write(s3)
				fout.write("\n")
			
			check_ready_printlines(f,fout,line)
		
		check_nodeStatus(command_output)
		fout.write("\n")
	

	#Heena admin show environment trace
	def admin_trace(command_output):
		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()
		tempStr = ""
				
		
		while not("GMT" in currentLine or "PST" in currentLine):
			tempStr += currentLine
			currentLine = filePtr.readline()
		
		tempStr = tempStr.replace('\n','')
		fout.write(tempStr)
		tempStr = currentLine
		currentLine = filePtr.readline()
		fout.write('\n')
		fout.write(tempStr)
		fout.write('\n')
		currentLine = filePtr.readline()

		nameOfDevice = fname.split('\\')[2]
		dateOfDevice = nameOfDevice.split('_')[1]
		dateOfDevice = dateOfDevice[:-4]
		date = datetime(year=int(dateOfDevice[4:8]), month=int(dateOfDevice[0:2]), day=int(dateOfDevice[2:4]))
		date0 = date.strftime("%b %d")
		# date -= timedelta(days = 1)
		# date1 = date.strftime("%b %d")
		# date -= timedelta(days = 1)
		# date2 = date.strftime("%b %d")

		while (currentLine):

			currentLine1 = currentLine.split()
			if (currentLine1[0] == str(date0[0:3])):
				if(currentLine1[1] == str(date0[4: len(date0)])):
					fout.write(currentLine)
				
			# if (currentLine1[0] == str(date1[0:3])):
				# if(currentLine1[1] == str(date1[4: len(date1)])):
					# fout.write(currentLine)
				
			# if (currentLine1[0] == str(date2[0:3])):
				# if(currentLine1[1] == str(date2[4: len(date2)])):
					# fout.write(currentLine)
				
			currentLine = filePtr.readline()

	#Heena for admin show environment voltage
	#Includes compare voltage,getSharedKeys,
	################################################
	# Give set of keys which are common in 2 dictionaries
	def getSharedKeys(dictNodeTable, dictNodeVolt):
		sharedKey = set(dictNodeTable.keys()).intersection(set(dictNodeVolt.keys()))
		return sharedKey


	# Compare 2 dictionaries
	def compareVoltage(dictNodeTable, dictNodeVolt):
		
		global tempStartStrVolt
		fout.write(tempStartStrVolt)
		combinedNode = getSharedKeys(dictNodeTable, dictNodeVolt)
		finalComparision = {}
		flag = 0

		for k in combinedNode:
			combinedAttribute = getSharedKeys(dictNodeTable[k], dictNodeVolt[k])

			for k1 in combinedAttribute:

				for l, h in dictNodeTable[k][k1].items():
					if(int(dictNodeVolt[k][k1]) < int(l) or int(dictNodeVolt[k][k1]) > int(h)):
						if (flag == 0):
							fout.write('R/S/I \t') 
							fout.write('Sensor \t\t\t')
							fout.write('(mV) \n')
							fout.write('------------------------------------------------\n')
							flag = 1
						
						fout.write(k)
						fout.write('\t')
						fout.write(k1)
						if(len(k1) > 14):
							fout.write('\t')
						elif(len(k1) < 7):
							fout.write('\t\t\t')
						else:
							fout.write('\t\t')
							
						fout.write(dictNodeVolt[k][k1])
						fout.write('\n')
		fout.write('\n')


	def admin_show_environment_table(command_output):

		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()

		while(currentLine.find('/*') == -1):
			currentLine = filePtr.readline()

		while (currentLine):

			if(currentLine != '\n' and currentLine.find('host') == -1 and currentLine.find('/*') != -1):
				node = currentLine.replace('\n', '')
				currentLine = filePtr.readline()
				dictHL = {}
				dictAttributeTable = {}

			if(currentLine.find('host') != -1):

				text = currentLine.split()
				text = text[0:6]
				currentLine = str(text)

				for ch in ['\\','`','*','{','}','[',']','(',')',',','#','+','-','.','!','/ ', '/' ,'$','\'']:
					currentLine = currentLine.replace(ch," ")
				text = currentLine.split()
				
				low = 0
				high = 0
				attribute = text[1]
				if(len(text) == 4):
					if(int(text[2]) >= int(text[3])):
						low = text[3]
						high = text[2]
					elif(int(text[2]) < int(text[3])):
						low = text[2]
						high = text[3]
						
					if(low != 0 and high != 0):
						dictHL.update({low: high})
						dictAttributeTable.update({attribute: dictHL})
						dictNodeTable.update({node: dictAttributeTable})

			currentLine = filePtr.readline()
			low = 0
			high = 0
			dictHL = {}
		if(len(dictNodeTable) != 0 and len(dictNodeVolt) != 0):
			compareVoltage(dictNodeTable, dictNodeVolt)

	def admin_show_environment_voltage(command_output):
		
		global tempStartStrVolt
		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()

		while not("GMT" in currentLine or "PST" in currentLine):
			tempStartStrVolt += currentLine
			currentLine = filePtr.readline()

		if(tempStartStrVolt.find('\n') != -1):
			tempStartStrVolt = tempStartStrVolt.replace('\n', '')
#		fout.write(tempStartStrVolt)
#		fout.write('\n')
		tempStartStrVolt += '\n'+currentLine+'\n'
#		fout.write(tempStartStrVolt)
#		fout.write('\n')
		currentLine = filePtr.readline()

		while(currentLine.find('/*') == -1):
			currentLine = filePtr.readline()

		while (currentLine):
			if(currentLine != '\n' and currentLine.find('host') == -1 and currentLine.find('/*') != -1):
				node = currentLine.replace('\n', '')
				currentLine = filePtr.readline()
				dictAttributeVolt = {}

			if(currentLine.find('host') != -1):
				text = currentLine.split()
				attribute = text[1]
				volt = text[2]
				dictAttributeVolt.update({attribute: volt})
				dictNodeVolt.update({node: dictAttributeVolt})

			currentLine = filePtr.readline()
		
		if(len(dictNodeTable) != 0 and len(dictNodeVolt) != 0):
			compareVoltage(dictNodeTable, dictNodeVolt)
	#############################################################

	
	#Heena admin show environment fans
	def admin_fans(command_output):
		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()
		tempStr = ""

		while not("GMT" in currentLine or "PST" in currentLine):
			tempStr += currentLine
			currentLine = filePtr.readline()

		tempStr = tempStr.replace('\n','')
		fout.write(tempStr)
		tempStr = currentLine
		fout.write('\n')
		fout.write(tempStr)
		currentLine = filePtr.readline()
		fout.write('\n')
		tempStr = ""

		while(currentLine.find("FT") == -1):
			tempStr += currentLine
			currentLine = filePtr.readline()

		tempStrSpeed = ""
		tempStrTime = ""
		tempStr2 = ""
		result = ""

		while currentLine:

			if (currentLine.find('Speed') != -1):
				tempStrSpeed += currentLine
				currentLine = filePtr.readline()
				tempStr2 = currentLine
				tempStrSpeed += tempStr2
				
				tempStr2 = tempStr2.split()
				for i in range(len(tempStr2)):
					
					if (int(tempStr2[i]) < 3000 or int(tempStr2[i]) > 5000):
						tempStrSpeed += filePtr.readline()
						tempStrSpeed += filePtr.readline()
						break
				
				if (i == len(tempStr2) - 1):
					tempStrSpeed = " "
				else:
					result += tempStrSpeed
					
			currentLine = filePtr.readline()
			tempStrSpeed = ""
		if result:
			fout.write(tempStr)
			fout.write(result)
		fout.write("\n")

	#Heena admin show environment power
	def admin_power(command_output):
		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()
		tempStr = ""

		while not("GMT" in currentLine or "PST" in currentLine):
			tempStr += currentLine
			currentLine = filePtr.readline()
		
		tempStr = tempStr.replace('\n','')
		fout.write(tempStr)
		tempStr = currentLine
		currentLine = filePtr.readline()
		fout.write('\n')
		fout.write(tempStr)
		fout.write('\n')
		tempStr = ""
		tempRes = ""
		result = ""
		
		while (currentLine.find('/*') == -1):
			tempStr += currentLine
			currentLine = filePtr.readline()
		
		while (currentLine.find('Power Supply') == -1):
			if(currentLine.find('/*')):
				tempRes = currentLine
				currentLine = filePtr.readline()
				
			if(currentLine.find('host') != -1 and currentLine.find('Ok') == -1):
				tempRes += currentLine
				currentLine = filePtr.readline()
				result += tempRes

		if result:
			fout.write(tempStr)
			fout.write(result)

	#Heena show drops

	def show_drops(todaysFile, prevDayFile):
	# Compare the attribute of 2 dictionaries and give those row having diff values
		def compareAttributes(currentDict, oldDict):
			sharedKey = set(currentDict.keys()).intersection(set(oldDict.keys()))		# sharedKey contains key common in both the dict
			combined = defaultdict(int)
					
			for key in sharedKey :
				if currentDict[key] != oldDict[key]:
					combined[key] = [int(currentDict[key]) - int(oldDict[key])]
					combined[key].append(currentDict[key])
						
			sharedKeyCurrent = set(currentDict.keys()).difference(sharedKey)			# keys in currentDict but not in sharedKey
			for key in sharedKeyCurrent :
				combined.update({key : {currentDict[key] : currentDict[key]}})
			
			
			sharedKeyPrev = set(oldDict.keys()).difference(sharedKey)					# keys in oldDict but not in sharedKey
			for key in sharedKeyPrev :
				oldDict[key] = -1 * int(oldDict[key])
				combined.update({key : {oldDict[key] : 'NA'}})
			
			return combined

		# Give set of keys which are common in 2 dictionaries
		def getSharedKeys(currentDict, oldDict):
			sharedKey = set(currentDict.keys()).intersection(set(oldDict.keys()))
			return sharedKey

		tempStrHeading = ""

		# Compare 2 dictionaries
		def compareDictionaries(currentDict, oldDict):
			combinedNode = getSharedKeys(currentDict, oldDict)
			finalComparision =  {}
			global tempStrHeading
			
			for k in combinedNode:
				combinedNPFIA = getSharedKeys(currentDict[k], oldDict[k])
				fout.write('----------------------------------------------------------\n')
				fout.write('\n\t\t\t'+k+'\t\t\t\n')
				for k1 in combinedNPFIA:
					if (currentDict[k][k1]):
						combinedAttribute = getSharedKeys(currentDict[k][k1], oldDict[k][k1])
						finalComaprision = compareAttributes(currentDict[k][k1], oldDict[k][k1])
						
						if len(finalComaprision) != 0:
							fout.write('\n----------------------------------------------------------\n')
							fout.write(k1)
							fout.write("\t\t\tTODAYS-VALUE\t DELTA ")
							fout.write('\n----------------------------------------------------------')
							fout.write("\n")
							
							for key, value in finalComaprision.items():
								fout.write(key)
								if(len(key) > 23):
									fout.write('\t')
								else:
									fout.write('\t\t')
								tempstr = str(finalComaprision[key])
								if (tempstr.find("'")):
									tempstr = tempstr.replace("'", '')
								if (tempstr.find('{}')):
									tempstr = tempstr.strip('{}')
								if (tempstr.find('[]')):
									tempstr = tempstr.strip('[]')
								if (tempstr.find(':')):
									tempstr = tempstr.replace(':', '\t')
								if (tempstr.find(',')):
									tempstr = tempstr.replace(',', '\t')
								
								tempstr2 = tempstr.split()
								fout.write(tempstr2[len(tempstr2) - 1])
								fout.write('\t\t')
								fout.write(tempstr2[0])
								fout.write('\n')

		# Serialize the file data to dictionary                
		def fillDictionary(fileName):
			currentFile = open(fileName, "r")    
			nodeDict =  {}
			upperNodeLine = ""
			attributeDict =  {}
			nodeLine = ""
			currentLine = currentFile.readline()
			
			while currentLine :
				
				if(currentLine.find('Node') != -1):
					arrtibuteDict =  {}
					tempStrToReadLine = " "
					npFiaDict =  {}
					currentLine = currentLine.rstrip()
					currentLine = currentLine.lstrip()
					upperNodeLine = currentLine
				if (currentLine.find('NP') != -1):
					nodeLine = currentLine.strip()
					currentLine = currentFile.readline()
					if(currentLine.find('-------') != -1):
						currentLine = currentFile.readline()
						while currentLine:
							tempStrToReadLine = currentLine.split()
							attributeDict.update({tempStrToReadLine[0] : tempStrToReadLine[1]})
							currentLine = currentFile.readline()
							if(currentLine.find('-----') != -1):                    
								npFiaDict.update({nodeLine : attributeDict})
								nodeDict.update({upperNodeLine : npFiaDict})
								attributeDict =  {}
								break
				else:
					if (currentLine.find('FIA') != -1 and currentLine.find('No') != -1):
						npFiaDict.update({currentLine.strip() : ''})
						
					elif(currentLine.find('FIA') != -1):
						nodeLine = currentLine.strip()
						currentLine = currentFile.readline()
						if(currentLine.find('-------') != -1):
							currentLine = currentFile.readline()
							while currentLine:
								tempStrToReadLine = currentLine.split()
								attributeDict.update({tempStrToReadLine[0] : tempStrToReadLine[1]})
							
								currentLine = currentFile.readline()
								if(currentLine.find('-----') != -1):
									npFiaDict.update({nodeLine : attributeDict})
									nodeDict.update({upperNodeLine : npFiaDict})
									attributeDict =  {}
									break
				currentLine = currentFile.readline()
			return (nodeDict)

		currentFile = open(todaysFile, 'r')
		currentLine = currentFile.readline()
		tempStart = ""
		
		while not("GMT" in currentLine or "PST" in currentLine):
			tempStart += currentLine
			currentLine =  currentFile.readline()
			if(tempStart.find('\n') != -1):
				tempStart = tempStart.replace('\n', '')
		tempStart += '\n'+currentLine+'\n'
		fout.write(tempStart)
		currentFile.close()
	
		todaysFileDict = fillDictionary(todaysFile)
		prevDayFileDict = fillDictionary(prevDayFile)
		compareDictionaries(todaysFileDict, prevDayFileDict)
		
		
	#Heena show cef tables
	#calculate the (C, D) != (Y, N) combination
	def show_cef_tables(command_output):

		filePtr = open (command_output, "r")
		line = filePtr.readline()
		splitLine = ""
		appendLines = ""
		startLine = line
		countYN = 0
		tempStartStr = ""

		while not ("GMT" in line or "PST" in line):
			tempStartStr += line
			line = filePtr.readline()
    
		if(tempStartStr.find('\n') != -1):
			tempStartStr = tempStartStr.replace('\n', '')
		fout.write(tempStartStr)
		fout.write('\n')
		fout.write(line)
		line = filePtr.readline()
    
		# Read lines untill u find Table ID
		while(line.find('Table ID') == -1):
			appendLines += line
			line = filePtr.readline()
		appendLines += line
		line = filePtr.readline()

		# Now you are reading table, check until you find next command
		while line:
			splitLine = re.sub(r'\s+', '', line)
        
			if ((splitLine[-5] == 'Y') or (splitLine[-6] == 'N')): 
				appendLines += line
				countYN += 1
			line = filePtr.readline()

		if(appendLines.count('\n') > 7 and countYN != 0):
			fout.write(appendLines)
		fout.write("\n")


	#Heena show watchdog memory-state location all
	def show_watchdog_memory_state_location_all(command_output):

		filePtr = open (command_output, "r")
		currentLine = filePtr.readline()
		tempStr = ""
		tempStartStr = ""
		countNormal = 0

		while not("GMT" in currentLine or "PST" in currentLine):
			tempStartStr += currentLine
			currentLine = filePtr.readline()

		if(tempStartStr.find('\n') != -1):
			tempStartStr = tempStartStr.replace('\n', '')
		fout.write(tempStartStr)
		fout.write('\n')
		fout.write(currentLine)
		
		currentLine = filePtr.readline()

		while currentLine:

			if (currentLine.find('node') != -1):
				tempStr += currentLine
				currentLine = filePtr.readline()
            
				if (currentLine.find('Memory') != -1):
					tempStr += currentLine
					currentLine = filePtr.readline()

					if (currentLine.find('Physical') != -1):
						tempStr += currentLine
						currentLine = filePtr.readline()

						if (currentLine.find('Free') != -1):
							tempStr += currentLine
							currentLine = filePtr.readline()

							if (currentLine.find('Normal') == -1):
								tempStr += currentLine
								countNormal += 1
								currentLine = filePtr.readline()
							else:
								tempStr = ""
								currentLine = filePtr.readline()

			if (tempStr.count('\n') > 0):
				fout.write(tempStr)
				tempStr = ""
		fout.write("\n")


	#Heena show cef resource hardware ingress location<>
	def show_cef_resource_hardware_ingress_location(command_output):
		filePtr = open(command_output, "r")
		currentLine = filePtr.readline()
		count = 0
		tempStr = ""

		while not("GMT" in currentLine or "PST" in currentLine):
			tempStr += currentLine
			currentLine = filePtr.readline()

		tempStr = tempStr.replace('\n','')
		fout.write(tempStr)
		fout.write('\n')
		fout.write(currentLine)
		currentLine = filePtr.readline()
		tempStr = ""

		while currentLine:
			if (currentLine.find('GREEN') == -1 and currentLine.find('\n') == -1):
				count += 1
				tempStr += currentLine
	
			currentLine = filePtr.readline()

		if (count > 1):
			fout.write(tempStr)
			
		fout.write("\n")


	#Added from existing NCS6k code. show_log
	def show_logging_start(command_output):
		parser = open(command_output, 'r')
		
		# temp_list has the known/ non-impacting logs that can be removed.
		temp_file=open('loggingfilequotes.txt','r')
		temp_list=[]
		#print (temp_list)
		for l in temp_file:
			if(len(l)>1):
				temp_list.append(l.strip())
	  #print (l)
		#print (temp_list)
		temp_file.close()
		##temp_list = ##["%L2-PLIM_ETHER-2-RX_RF","%PKT_INFRA-LINK-3-UPDOWN","%PKT_INFRA-LINEPROTO-5-UPDOWN","%L2-BM-5-MBR_BFD_NOT_RUNNING","%L2-BM-6-ACTIVE","%L2-BFD-6-SESSION_REMOVED",
		##"panini_spio_fill_bdl_mbr_info:"]
		
		
		flag = 0
		for curline in parser:
			for f in temp_list:
				if f in curline:
					flag = 1
			if flag == 0:
				fout.write(curline)
			else:	
				flag = 0
		fout.write('\n\n')
		
	
	#########################################################################################################################
	def getPrevFileLocation(cmd_extract):
		nameOfDevice = fname.split('\\')[2]
		
		dateOfDevice = nameOfDevice.split('_')[1]
		dateOfDevice = dateOfDevice[:-4]
		prevNoOfDays = 1
		date = datetime(year=int(dateOfDevice[4:8]), month=int(dateOfDevice[0:2]), day=int(dateOfDevice[2:4]))
		for dateRange in range(prevNoOfDays):
			date -= timedelta(days = prevNoOfDays)
			prevDate = date.strftime("%m%d%Y")
			fileLocation = dASR9k+"\\TMO_Outputs\ASR9k_"+prevDate+"\Historic\\"+fname.split('\\')[2].split('-')[0][:-13]+"\\"+cmd_extract+".txt"
			if (os.path.exists(fileLocation)):
				return fileLocation
			else:
				continue;
		return 0



	#Function to call the corressponding function for the command in cmd_extract
	def fn_parse_command(command_output,cmd_extract):
		# print(cmd_extract)
		global command_count
		global alarmraised
		global redundancyraised
		global status
		#print('alaramraised in fn")
		#print(alaramraised)
		if (("admin show platform" in cmd_extract)):
			try:
				admin_show_platform(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
				
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
				
				
		elif (("show cef platform oor location" in cmd_extract)):
			try:
				show_cef_platform(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show controllers np soft-errors all all" in cmd_extract)):
			try:
				show_controllers(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show memory summary location all" in cmd_extract) ):
			try:
				show_memory(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show hw-module fpd location all" in cmd_extract) ):
			try:
				show_hw_module(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show l2vpn forwarding resource detail location" in cmd_extract) ):
			try:
				show_l2vpn_forwarding(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show processes memory detail" in cmd_extract) ):
			try:
				show_processes_memory(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show cef resource hardware ingress location" in cmd_extract) ):
			try:
				show_cef_resource_hardware_ingress_location(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show cef tables" in cmd_extract) ):
			try:
				show_cef_tables(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show watchdog memory-state location all" in cmd_extract) ):
			try:
				show_watchdog_memory_state_location_all(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show health sysdb" in cmd_extract) ):
			try:
				sysdb(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show health gsp" in cmd_extract) ):
			try:
				show_gsp(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show redundancy" in cmd_extract) ):
			try:
				show_redundancy(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show logging start" in cmd_extract) or ("show logging" in cmd_extract) or ("sh logging" in cmd_extract) or ("sh log" in cmd_extract) or ("show log" in cmd_extract)):
			try:
	      #print()
				show_logging_start(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
		
		elif (("show asic-errors all location" in cmd_extract)):
			try:
				getLocationName = getLocation(command_output)
				commandWithLocation = cmd_extract+"_"+getLocationName[:-1]
				commandWithLocation = commandWithLocation.replace('/', '-')
				copyForHistoric(command_output,commandWithLocation)
				prevFileLocation = getPrevFileLocation(commandWithLocation)
				
				if(prevFileLocation != 0):
						show_asic(command_output,prevFileLocation)
						flogs.write("\n"+commandWithLocation+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+commandWithLocation+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show pfm location all" in cmd_extract)):
			try:
				copyForHistoric(command_output,cmd_extract)
				prevFileLocation = getPrevFileLocation(cmd_extract)
				if(prevFileLocation != 0):
						show_pfm(command_output,prevFileLocation)
						flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
								
		
		elif (("show drops" in cmd_extract)):
			try:
				prevFileLocation = getPrevFileLocation(cmd_extract)
				copyForHistoric(command_output,cmd_extract)
				if(prevFileLocation != 0):
						show_drops(command_output,prevFileLocation)
						flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("show l2vpn bridge-domain summary" in cmd_extract)):
			try:
				prevFileLocation = getPrevFileLocation(cmd_extract)
				copyForHistoric(command_output,cmd_extract)
				if(prevFileLocation != 0):
						show_l2vpn_bridge(command_output,prevFileLocation)
						flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("admin show reboot history" in cmd_extract)):
			try:
				getLocationName = getLocation(command_output)
				commandWithLocation = cmd_extract+"_"+getLocationName[:-1]
				commandWithLocation = commandWithLocation.replace('/', '-')
				prevFileLocation = getPrevFileLocation(commandWithLocation)
				copyForHistoric(command_output,commandWithLocation)
				if(prevFileLocation != 0):
						show_reboot(command_output,prevFileLocation)
						flogs.write("\n"+commandWithLocation+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+commandWithLocation+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
		
		elif (("show lpts pifib hardware police location" in cmd_extract)):
			try:
				getLocationName = getLocation(command_output)
				commandWithLocation = cmd_extract+"_"+getLocationName[:-1]
				commandWithLocation = commandWithLocation.replace('/', '-')
				prevFileLocation = getPrevFileLocation(commandWithLocation)
				copyForHistoric(command_output,commandWithLocation)
				if(prevFileLocation != 0):
						show_lpts(command_output,prevFileLocation)
						flogs.write("\n"+commandWithLocation+": Parsed Successfully")
				else:
					printinfout(command_output)
					flogs.write("\n"+commandWithLocation+": Parsed Successfully")
			
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("show prm server tcam summary all all all location" in cmd_extract)):
			try:
				show_prm_server(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
								
				
		elif (("admin show environment temperature" in cmd_extract)):
			try:
				admin_temperature(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"				
				
				
		elif (("admin show environment leds" in cmd_extract)):
			try:
				admin_leds(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("admin show environment fans" in cmd_extract)):
			try:
				admin_fans(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"				
				
				
		elif (("admin show environment power-supply" in cmd_extract)):
			try:
				admin_power(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
				
		elif (("admin show environment trace" in cmd_extract)):
			try:
				admin_trace(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("admin show environment voltage" in cmd_extract)):
			try:
				
				admin_show_environment_voltage(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
		
		elif (("admin show environment table" in cmd_extract)):
			try:
				admin_show_environment_table(command_output)
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsed Successfully")
			except:
				# printinfout(command_output)
				command_count = command_count+1
				flogs.write("\n"+cmd_extract.strip("\n")+": Parsing Error")
				status = status + "\n"+cmd_extract.strip("\n")+": Parsing Error"
				
						
		else:
			printinfout(command_output)
			flogs.write("\n"+cmd_extract.strip("\n")+": Not analysed as of now")
			status = status + "\n"+cmd_extract.strip("\n")+": Not analysed as of now"
			
		
						
		

	#Common function to print the whole output of a particular command in the fout file
	def printinfout(command_output):
		pa=open(command_output,'r')
		for l in pa:
			fout.write(l)
		fout.write('\n\n')
		
	#Function to parse the whole file and create seperate temp files in temp folders on the basis of the command + its location.	
	def parsefiles(command_output):
		unknownCommands = ""
		unknownCommandsPresent = 0
		# print("Entering Parse FIles")
		full_parse = open(command_output, "r")
		# alllines=full_parse.readlines()
		alllines=""
		#THis is to remove show platform from the output file
		for line in full_parse:
			if("#show platform" in line):
				while not("#admin show platform" in line):
					line = full_parse.readline()
			alllines = alllines + line
			
		alllines=[i.replace("\x08","") for i in alllines]
		alllines=[i.replace("\x1b","") for i in alllines]
		full_parse.close()


		full_parse = open('cleantemp.txt', 'w')
		for cl in alllines:
			full_parse.write(cl)
		full_parse.close()

		pattern=""
		full_parse = open('cleantemp.txt', 'r')
		#print("LOGS:\n")
		for line in full_parse:

			if "RP/" in line:
				#print(line)
				pattern = line.split('#')[0]
				print(pattern)
				break
		full_parse.close()

		full_parse = open('cleantemp.txt', "r")

		pattern2=""
		#print("LOGS:\n")
		for line in full_parse:

			if "sysadmin" in line:
				pattern2 = line.split()[0][line.split()[0].find('sysadmin'):-1]
				print(pattern2)
				break
		full_parse.close()
		
		parser = open('cleantemp.txt','r')
		#print(len(pattern))
		#print(len(pattern2))
		pattern1pos=[]
		pattern2pos=[]
		lines=parser.readlines()

		pattern1pos=[n for n,line in enumerate(lines) if ((pattern in line) and len(pattern)!=0)]
		pattern2pos=[n for n,line in enumerate(lines) if ((pattern2 in line) and len(pattern2)!=0)]
		#print(pattern1pos)
		#print('\n\n')
		#print(pattern2pos)
		patternpos=pattern1pos+pattern2pos
		patternpos.sort()
		comlin=open('commandslines.txt','r')
		dict_comm=comlin.readlines()
		# print(dict_comm)
		dictionary={}
		#print (len(patternpos)+1)
		
		for pn in range(0,len(patternpos)+1):
			if((pn-1)<0):
				edit=lines[0:patternpos[pn]]
			elif((pn+1)<=len(patternpos)):
				edit=lines[patternpos[pn-1]:patternpos[pn]]
			else:
				edit=lines[patternpos[pn-1]:]
			commfound=False
			if(len(edit)>0):
				for command in dict_comm:
					command=command.strip()
							
					dictionary[command]=[]
					if(command in ''.join(edit)):
						# print(command+"\tFOUND\t"+str(pn)+'\n')
						cfile=open(".\\temp\\"+str(pn)+'.txt','w')
						commfound=True
						for l in edit:
							cfile.write(l)
						cfile.close()
						dictionary[command].append(edit)
						# print(command)
						# print("***************************************************************")
						# print(str(pn))
						fn_parse_command(".\\temp\\"+str(pn)+'.txt',command)
						break
				# print(edit)
				if(commfound==False):
					unknownCommandsPresent = 1
					for l in edit:
						unknownCommands = unknownCommands + l
					# fout.write('\n\n')
		if(unknownCommandsPresent == 1):
			fout.write("***************************************************************************************\n")
			fout.write("*                  THE FOLLOWING COMMANDS HAVE TO BE PARSED MANUALLY                  *\n")
			fout.write("***************************************************************************************\n")
			fout.write(unknownCommands)
		return


	alarmraised=True
	redundancyraised=True
	fname = sys.argv[1]
	os.chdir('..')#Moving one folder up
	dASR9k = os.path.abspath(os.curdir)
	os.chdir(".\\HealthCheckScripts")
	#print("***********************")
	#print(fname)
	#print("******************************")
	timestamp = sys.argv[2]
	flogs = open(".\\Output\\Logs_"+fname.split('\\')[-1].split('.')[0]+"_parsed.txt","w")
	flogs.write("\n"+"Executing "+fname)
	statusUpdate.write("\n"+"Executed "+fname)

	fout = open(".\\Output\\"+fname.split('\\')[-1].split('.')[0]+"_parsed.txt","a")
	parsefiles(fname)				
	if not("Error" in status):
		statusUpdate.write(" All commands executed successfully")
	else:
		statusUpdate.write(status)
	fout.close()
	flogs.close()
	#full_parse.close()




	cmd_return = subprocess.Popen("del temp2.txt", shell = True)
	cmd_return.wait()
	cmd_return = subprocess.Popen("del cleantemp.txt", shell = True)
	cmd_return.wait()
	print("\n##############"+fname+" parsed. Check logs to see errors if any.##############")

	#time.sleep(3)
	cmd_return = subprocess.Popen("del .\\temp\\*.txt", shell = True)
	cmd_return.wait()
	
except:
	fout.close()
	#full_parse.close()
	flogs.close()
	print("\n***************Something went wrong with parsing "+fname+". Kindly notify the developer and check it manually for the time being******************")
	statusUpdate.write("\n***************Something went wrong with parsing "+fname+". Kindly notify the developer and check it manually for the time being******************")
	
	
