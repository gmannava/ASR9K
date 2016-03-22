import os
import os.path
import shutil

processed = []

for dirpath, dirnames, filenames in os.walk("./TMO_Outputs"):
	for filename in filenames:
		if not("Historic" in dirpath):
			if (filename.endswith(".txt") and not ("_" in filename)):
				directory = dirpath.strip('.//').split('\\')[1]
				date = directory.split('_')[1]
				dirnam = filename.strip('.txt')
				if not os.path.exists("../TMO_HealthTrends/NodeWiseTMOOutputs/"+dirnam):
					os.makedirs("../TMO_HealthTrends/NodeWiseTMOOutputs/"+dirnam)
				os.rename(dirpath+"\\"+filename, dirpath+"\\"+filename.split('.')[0]+"_"+date+".txt")
				shutil.copy2(dirpath+"/"+filename.split('.')[0]+"_"+date+".txt", "../TMO_HealthTrends/NodeWiseTMOOutputs/"+dirnam)
				
