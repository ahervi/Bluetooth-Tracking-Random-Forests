import csv
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random
import difflib
import math
import numbers
import pickle
import operator
import itertools
import math
import datetime


def probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3, clf3_4, X, X1, X2, X3, X4):
	YpredictionConsecutiveSignal = []
	limitTestSampleFinal = int(math.floor(int(len(X1)*sizeTest)))
	probas3_1 = clf3_1.predict_proba(X1)
	probas3_2 = clf3_2.predict_proba(X2)
	probas3_3 = clf3_3.predict_proba(X3)
	probas3_4 = clf3_4.predict_proba(X4)

	probas4 = clf4.predict_proba(X)

	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas4[i][j]+probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal

def probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_4, X1, X2, X3, X4):
	YpredictionConsecutiveSignal = []
	probas3_1 = clf3_1.predict_proba(X1)
	probas3_2 = clf3_2.predict_proba(X2)
	probas3_3 = clf3_3.predict_proba(X3)
	probas3_4 = clf3_4.predict_proba(X4)
	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal

def rssiWithHumidity(timestamp, rssi):
	res = math.cos((2*math.pi*float(timestamp2hour(timestamp))-1)/24)
	if res < -0.5:		
		res = -0.5
	return rssi + res
def timestamp2hour(timestamp):
	return int(datetime.datetime.fromtimestamp(int(timestamp)).strftime('%H'))


def givesYshould(sizeTest, X, Y):
	limitTestSample = int(math.floor(int(len(X)*sizeTest)))
	return Y[limitTestSample:]

def givesClassifier(ID, Xcombi, Xfinal, Ycombi, Yfinal, sizeTest):

	clf4 = RandomForestClassifier(n_estimators=100)
	
	limitTestSampleCombi = int(math.floor(int(len(Xcombi)*sizeTest)))
	limitTestSampleFinal = int(math.floor(int(len(Xfinal)*sizeTest)))

	clf4 = clf4.fit(Xcombi[:limitTestSampleCombi], Ycombi[:limitTestSampleCombi])

	Ypred4 = clf4.predict(Xfinal[limitTestSampleFinal:])
	Yshould = Yfinal[limitTestSampleFinal:]
	ratio4 = 0
	dicDB = dict()
	for db in DBS:
		dicDB[db[2]] = 0

	for j in range(len(Ypred4)):
		if Yshould[j] == Ypred4[j]:
			ratio4 += 1
		else:
			dicDB[Yshould[j]] += 1
	errors4= ratio4
	ratio4 = float(ratio4)

	ratio4 = ratio4 / len(Yshould)
	print("Similarity percentile : " + str(ratio4))
	print(str(len(Yshould)- errors4) + " errors ( " + str(100-100*float(errors4)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(Xfinal[:limitTestSampleFinal])) + " training samples (total " + str(len(Yfinal)) +" ) : " + str(dicDB))
	with open("randomForestModel" + str(ID) ,"wb") as f:
		pickle.dump(clf4, f)
	return clf4, Ypred4

def givesTriList(list):
	res1 = []
	res2 = []
	res3 = []
	res4 = []

	for l in list:
		res1.append([l[0],l[1],l[2]])
		res2.append([l[0],l[1], l[3]])

		res3.append([l[0], l[2],l[3]])
		res4.append([l[1],l[2],l[3]])
	res = [res1, res2, res3, res4]
	return res

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

	#Debut du test de combiaison
	ultiList = []
	for p in range(len(finalList) - 1):
		liste1 = finalList[p]
		liste2 = finalList[p+1]
		combi = []
		i = 0
		MAX = len(liste1)

		for z in range(len(liste1)):
			for e in range(len(liste1)):
				for r in range(len(liste1)):
					temp = [elem for elem in liste1]
					temp[z] = liste2[z]
					temp[e] = liste2[e]
					temp[r] = liste2[r]
					combi.append(temp)

		combi.sort()
		combi = list(combi for combi,_ in itertools.groupby(combi))
		combi.insert(0, liste2)
		combi.insert(0, liste1)

		ultiList.extend(combi)
	#print(lengthBefore)
	#print(lengthAfter)
	return [ultiList, givesTriList(ultiList), finalList, givesTriList(finalList)]


# CHANGE DB NAMES HERE
DB_NAMES = ["MONDAYWEEK4AFTERNOON","TUESDAYWEEK4MORNING", "TUESDAYWEEK4AFTERNOON","WEDNESDAYWEEK4MORNING", "WEDNESDAYWEEK4AFTERNOON", "THURSDAYWEEK4MORNING","THURSDAYWEEK4AFTERNOON"]
for DB_NAME in DB_NAMES:
	Xfinal = []
	Xfinal1 = []
	Xfinal2 = []
	Xfinal3 = []
	Xfinal4 = []
	Yfinal = []

	DBS = [[DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"], [DB_NAME, "F2:39:F2:6A:80:89", "fenetre_russia"], [DB_NAME, "C7:62:97:12:1E:35", "the"], [DB_NAME, "E4:FA:6E:AF:58:19", "carte_bancaire"]]
	for name in DBS:
		bigList = givesList(name[0]+".db", name[1])

		listefinal4 ,listefinal3_1, listefinal3_2, listefinal3_3, listefinal3_4= bigList[2], bigList[3][0], bigList[3][1], bigList[3][2], bigList[3][3], 

		Xfinal.extend(listefinal4)
		Xfinal1.extend(listefinal3_1)
		Xfinal2.extend(listefinal3_2)
		Xfinal3.extend(listefinal3_3)
		Xfinal4.extend(listefinal3_4)
		Yfinal.extend([name[2]]*len(listefinal4))	
	random.seed(1)
	b = range(len(Xfinal))

	random.shuffle(b)
	Xfinal = [Xfinal[i] for i in b] # or:
	Xfinal1 = [Xfinal1[i] for i in b] # or:
	Xfinal2 = [Xfinal2[i] for i in b] # or:
	Xfinal3 = [Xfinal3[i] for i in b] # or:
	Xfinal4 = [Xfinal4[i] for i in b] # or:

	Yfinal = [Yfinal[i] for i in b] # or:

	with open("randomForestModel4","r") as f:
	    clf4 = pickle.load(f)
	with open("randomForestModel3_1","r") as f:
	    clf3_1= pickle.load(f)
	with open("randomForestModel3_2","r") as f:
	    clf3_2 = pickle.load(f)
	with open("randomForestModel3_3","r") as f:
	    clf3_3 = pickle.load(f)
	with open("randomForestModel3_4","r") as f:
	    clf3_4 = pickle.load(f)
	sizeTest = 0.66
	Yshould = givesYshould(0, Xfinal, Yfinal)
	YpredictionConsecutiveSignal4 = clf4.predict(Xfinal)
	YpredictionConsecutiveSignal3_1 = clf3_1.predict(Xfinal1)
	YpredictionConsecutiveSignal3_2 = clf3_2.predict(Xfinal2)
	YpredictionConsecutiveSignal3_3 = clf3_3.predict(Xfinal3)
	YpredictionConsecutiveSignal3_4 = clf3_4.predict(Xfinal4)
	print("FINAL RESULTS")

	ratio = 0
	for k in range(len(YpredictionConsecutiveSignal4)):
		proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
		pos = str(YpredictionConsecutiveSignal4[k])

		if pos == Yshould[k]:
			ratio += 1
	errors = ratio
	ratio = float(ratio)
	ratio = ratio / len(Yshould)

	#print("Similarity percentile : " + str(ratio))
	#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
	print("Ratio with only 4model " + str((1-ratio)*100))

	for l in range(2):
	 	ratio = 0
		for k in range(len(YpredictionConsecutiveSignal4)):
			proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
			pos4 = str(YpredictionConsecutiveSignal4[k])
			pos3_1 = str(YpredictionConsecutiveSignal3_1[k])
			pos3_2 = str(YpredictionConsecutiveSignal3_2[k])
			pos3_3 = str(YpredictionConsecutiveSignal3_3[k])
			pos3_4 = str(YpredictionConsecutiveSignal3_4[k])
			proba[pos4] += l
			proba[pos3_1] += 1
			proba[pos3_2] += 1
			proba[pos3_3] += 1
			proba[pos3_4] += 1
			pos = max(proba.iteritems(), key=operator.itemgetter(1))[0]
			if pos == Yshould[k]:
				ratio += 1
		errors = ratio
		ratio = float(ratio)
		ratio = ratio / len(Yshould)

		#print("Similarity percentile : " + str(ratio))
		#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
		print("Ratio with 4model vote at " + str(l)+ " " + str((1-ratio)*100))

	YpredictionConsecutiveSignal = probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3, clf3_3, Xfinal, Xfinal1, Xfinal2, Xfinal3, Xfinal4)
	ratio = 0

	for k in range(len(YpredictionConsecutiveSignal)):
		if YpredictionConsecutiveSignal[k] == Yshould[k]:
			ratio += 1
	errors = ratio
	ratio = float(ratio)
	ratio = ratio / len(Yshould)

		#print("Similarity percentile : " + str(ratio))
		#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
	print("Ratio M + S proba " + str((1-ratio)*100))

	YpredictionConsecutiveSignal = probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_3, Xfinal1, Xfinal2, Xfinal3, Xfinal4)
	ratio = 0

	for k in range(len(YpredictionConsecutiveSignal)):
		if YpredictionConsecutiveSignal[k] == Yshould[k]:
			ratio += 1
	errors = ratio
	ratio = float(ratio)
	ratio = ratio / len(Yshould)

		#print("Similarity percentile : " + str(ratio))
		#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
	print("Ratio proba S " + str((1-ratio)*100))
