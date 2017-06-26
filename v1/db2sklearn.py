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
			if isinstance(row[4], numbers.Number) and row[4] < 1:

				if finalList[i][idAfter] == 0:
					finalList[i][idAfter] = row[4]
				else:
					finalList[i][idAfter] = float((row[4] + finalList[i][idAfter])) / 2
			
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
DBS = [["real", "C7:64:6C:03:B9:40", "me"], ["real", "C1:CF:31:F3:29:6C", "russia"], ["real", "DA:E7:8C:CA:05:CF", "fenetre_casque"], ["real", "F2:39:F2:6A:80:89", "fenetre_russia"], ["real", "C7:62:97:12:1E:35", "the"], ["real", "E4:FA:6E:AF:58:19", "carte_bancaire"]]
for name in DBS:
	liste = givesList(name[0]+".db", name[1])
	X.extend(liste)
	Y.extend([name[2]]*len(liste))	

random.seed(1)

Z = list(zip(X, Y))

random.shuffle(Z)

X, Y = zip(*Z)
RANGE = 10
for i in range(RANGE):
	clf = RandomForestClassifier(n_estimators=100)
	sizeTest1 = 1.0/float(RANGE) * (i)
	sizeTest2 = 1.0/float(RANGE) * (i + 1)
	if i ==0:
		sizeTest1 = 0

	if sizeTest1 != 1:
		limitTestSample1 = int(math.floor(int(len(X)*sizeTest1)))
		limitTestSample2 = int(math.floor(int(len(X)*sizeTest2)))
		clf = clf.fit(X[limitTestSample1:limitTestSample2], Y[limitTestSample1:limitTestSample2])
		Ypred = clf.predict(X[:limitTestSample1] + X[limitTestSample2:])
		Yshould = Y[:limitTestSample1] + Y[limitTestSample2:]
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
		print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " : " + str(dicDB))
	else:

		clf = clf.fit(X, Y)

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
		print(str(len(Yshould)- errors) + " errors on " + str(len(Yshould)) + " : " + str(dicDB))
	with open("randomForestModel" + str(i) ,"wb") as f:
		pickle.dump(clf, f)
