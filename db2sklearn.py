import csv
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random
import difflib
import math
def givesList(DB_NAME):
	
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
		cursor.execute("""select ID, NAME, BSSID, TIME_STAMP, RSSI from COMBINED WHERE BSSID = "F2:39:F2:6A:80:89" ORDER BY TIME_STAMP ASC""")
		rows = cursor.fetchall()
		liste = []

		for row in rows:
			liste.append([row[0], row[1].encode("ascii"), row[2].encode("ascii"), row[3], row[4]])

	#On a la liste ordonnee des rssi
	TIME_WINDOW = 15

	i = 0
	timeStampBefore = liste[i][3]
	idBefore = liste[i][0] - 1

	finalList = [[0]*MAXID]

	for row in liste:
		timeStampAfter = int(row[3])
		idAfter = row[0] - 1
		if timeStampAfter - timeStampBefore > TIME_WINDOW:
			finalList.append([0]*MAXID)
			i += 1
			timeStampBefore = timeStampAfter

		else:
			
			if finalList[i][idAfter] == 0:
				finalList[i][idAfter] = row[4]
			else:
				finalList[i][idAfter] = np.mean([row[4], finalList[i][idAfter]])
		
		idBefore = idAfter

	#lengthBefore = len(finalList)

	index2remove = []
	for i in range(len(finalList)):

		if 0 in finalList[i]:
			index2remove.append(i)

		for j in range(MAXID):
			if np.isnan(finalList[i][j]):
				index2remove.append(i)
	#delete all list entries with index in index2remove
	finalList = [ i for j, i in enumerate(finalList) if j not in index2remove]


	lengthAfter = len(finalList)
	#print(lengthBefore)
	#print(lengthAfter)


	return finalList
X = []
Y = []

# CHANGE DB NAMES HERE
DBS = ["the", "russia", "behind", "fantome"]
for name in DBS:
	liste = givesList(name+".db")
	X.extend(liste)
	Y.extend([name]*len(liste))	

random.seed(1)

Z = list(zip(X, Y))

random.shuffle(Z)

X, Y = zip(*Z)
clf = RandomForestClassifier(n_estimators=100)

sizeTest = 1
if sizeTest != 1:
	limitTestSample = int(math.floor(int(len(X)*sizeTest)))
	clf = clf.fit(X[:limitTestSample], Y[:limitTestSample])
	Ypred = clf.predict(X[limitTestSample:])
	Yshould = Y[limitTestSample:]

	ratio = 0
	dicDB = dict()
	for db in DBS:
		dicDB[db] = 0

	for j in range(len(Ypred)):
		if Yshould[j] == Ypred[j]:
			ratio += 1
		else:
			dicDB[Yshould[j]] += 1
	errors = ratio
	ratio = float(ratio)

	ratio = ratio / len(Yshould)
	print("Similarity percentile : " + str(ratio))
	print(str(len(Yshould)- errors) + " errors on " + str(len(Yshould)) + " : " + str(dicDB))
else:
	clf = clf.fit(X, Y)
	Ypred = clf.predict(X)
	Yshould = Y
	ratio = 0
	dicDB = dict()
	for db in DBS:
		dicDB[db] = 0

	for j in range(len(Ypred)):
		if Yshould[j] == Ypred[j]:
			ratio += 1
		else:
			dicDB[Yshould[j]] += 1
	errors = ratio
	ratio = float(ratio)

	ratio = ratio / len(Yshould)
	print("Similarity percentile : " + str(ratio))
	print(str(len(Yshould)- errors) + " errors on " + str(len(Yshould)) + " : " + str(dicDB))
