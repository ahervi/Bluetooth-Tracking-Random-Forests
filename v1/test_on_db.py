import csv
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random
import difflib
import math
import numbers
import pickle

def givesList(DB_NAME, BSSID):
	
	FILENAME = DB_NAME[:-3] + ".csv"


	with sqlite3.connect(DB_NAME) as conn:
		c = conn.cursor()
		c.execute("""select max(ID)from COMBINED""")
		maxId = c.fetchall()

		for id in maxId:
			MAXID = id[0]
		
		RSSIS = []
		RSSI_HEADER = []
		for i in range(MAXID):
			RSSI_HEADER.append("RPI" + str(i + 1))
		RSSIS.append(RSSI_HEADER)

		rssiContent = []


	with sqlite3.connect(DB_NAME) as conn:
		cursor = conn.cursor()
		cursor.execute("""select ID, NAME, BSSID, TIME_STAMP, RSSI from COMBINED WHERE BSSID = ? ORDER BY TIME_STAMP ASC""", (BSSID,))
		rows = cursor.fetchall()
		liste = []

		for row in rows:
			liste.append([row[0], row[1].encode("ascii"), row[2].encode("ascii"), row[3], row[4]])

	#We have the rssis list by rpis' id : [id, RSSI] -> liste
	TIME_WINDOW = 15


	#index of the liste containing the succesive RSSIs by id : [RSSI1, RSSI2, ... , RSSIIDMAX] -> finalList
	i = -1



	finalList = []
	list2Add = [0]*MAXID
	#Initialisation of the timers for each RPIS : 

	timersBefore = [0]*MAXID

	# initialisation of the timers:
	k = 0
	while 0 in timersBefore:
		timersBefore[liste[k][0] - 1] = liste[k][3]
		k += 1

	timersAfter = [0]*MAXID


	idRPI = liste[0][0] - 1
	#index of liste
	j = 0

	while j < len(liste):
		row = liste[j]
		timersAfter[idRPI] = int(row[3])
		idRPI = row[0] - 1

		if isinstance(row[4], numbers.Number) and row[4] < 1:

			#If there have not been an update from all RPIS in the TIME_WINDOW : abandon of current index 
			# One of the RPIS have not manifested himself
			for l in range(MAXID):
				if timersAfter[idRPI] - timersBefore[l] > TIME_WINDOW and l != idRPI:
					list2Add[l] = 0
					timersBefore[l] = timersAfter[idRPI]

		
			list2Add[idRPI] = row[4]

			if not 0 in list2Add and (len(finalList) == 0 or (len(finalList) > 0 and list2Add != finalList[-1])): 
				temp = [0]*MAXID
				for m in range(MAXID):
					temp[m] = int(10 * list2Add[m]) / 10.0
				finalList.append(temp)
				i += 1
			timersBefore[idRPI] = timersAfter[idRPI]

		j+=1
	lengthAfter = len(finalList)
	#print(lengthBefore)
	#print(lengthAfter)
	return finalList

X = []
Y = []

# CHANGE DB NAMES HERE
DB_NAME = "combined"
DBS = [[DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"], [DB_NAME, "F2:39:F2:6A:80:89", "fenetre_russia"], [DB_NAME, "C7:62:97:12:1E:35", "the"], [DB_NAME, "E4:FA:6E:AF:58:19", "carte_bancaire"]]
for name in DBS:
	liste = givesList(name[0]+".db", name[1])
	X.extend(liste)
	Y.extend([name[2]]*len(liste))	

random.seed(1)
Z = list(zip(X, Y))

random.shuffle(Z)

X, Y = zip(*Z)
with open("randomForestModel0","r") as f:
    clf = pickle.load(f)

Ypred = clf.predict(X)
Yshould = Y
ratio = 0
dicDB = dict()
for db in DBS:
	dicDB[db[2]] = 0

for j in range(len(Ypred)):
	if Yshould[j] == Ypred[j]:
		ratio += 1
	else:
		dicDB[Yshould[j]] += 1
errors = ratio
ratio = float(ratio)

ratio = ratio / len(Yshould)
print("Similarity percentile : " + str(ratio))
print(str(len(Yshould)- errors) + " errors on " + str(len(Yshould)) + " : " + str(dicDB) + "/" + str(len([x for x in Y if x == "fenetre_russia"])))             

    
