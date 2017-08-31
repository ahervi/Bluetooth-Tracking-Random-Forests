import csv
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random
import difflib
import math
import numbers
import pickle
import matplotlib.pyplot as plt
import operator
import itertools
import math
import datetime
from matplotlib.font_manager import FontProperties
def timeseparation(XconsecutiveSignalCombinaisons, minutes):
	bufferRSSIS = []
	newXconsecutiveSignalCombinaisons = []
	oldTime = XconsecutiveSignalCombinaisons[0][1]
	for v in range(len(XconsecutiveSignalCombinaisons)):

		if XconsecutiveSignalCombinaisons[v][1] - oldTime > 60*minutes:
			oldTime = XconsecutiveSignalCombinaisons[v][1]
			newXconsecutiveSignalCombinaisons.append(bufferRSSIS)
			bufferRSSIS = []
		bufferRSSIS.append(XconsecutiveSignalCombinaisons[v][0])
	return newXconsecutiveSignalCombinaisons


#simule le comportement de traininglive
def rssiWithHumidity(timestamp, rssi):
	res = math.cos((2*math.pi*float(timestamp2hour(timestamp))-1)/24)
	if res < -0.5:		
		res = -0.5
	return rssi - res
def timestamp2hour(timestamp):
	return int(datetime.datetime.fromtimestamp(int(timestamp)).strftime('%H'))
def probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3, clf3_4, X, X1, X2, X3, X4, j):
	YpredictionConsecutiveSignal = []

	probas3_1 = clf3_1.predict_proba(X1[j])
	probas3_2 = clf3_2.predict_proba(X2[j])
	probas3_3 = clf3_3.predict_proba(X3[j])
	probas3_4 = clf3_4.predict_proba(X4[j])

	probas4 = clf4.predict_proba(X[j])

	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas4[i][j]+probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal

def probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_4, X1, X2, X3, X4, j):
	YpredictionConsecutiveSignal = []
	probas3_1 = clf3_1.predict_proba(X1[j])
	probas3_2 = clf3_2.predict_proba(X2[j])
	probas3_3 = clf3_3.predict_proba(X3[j])
	probas3_4 = clf3_4.predict_proba(X4[j])
	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal
def givesYshould(Y, j):
	
	return Y[j]

def givesClassifier(ID, DBS, XconsecutiveSignalCombinaisons, XconsecutiveSignal, YconsecutiveSignalCombinaisons, YconsecutiveSignal, sizeTest, j):
	b = range(len(XconsecutiveSignal[j]))
	random.shuffle(b)

	Xshuffled = [XconsecutiveSignal[j][i] for i in b] # or:
	Yshuffled = [YconsecutiveSignal[j][i] for i in b] # or:

	clf4 = RandomForestClassifier(n_estimators=100)

	clf4 = clf4.fit(Xshuffled, Yshuffled)
	YpredictionConsecutiveSignal4 = clf4.predict(Xshuffled)
	Yshould = Yshuffled
	ratio4 = 0
	dicDB = dict()
	for db in DBS:
		dicDB[db[2]] = 0


	rangeL = len(YpredictionConsecutiveSignal4)
	if rangeL > len(Yshould):
		rangeL = len(Yshould)

	for p in range(rangeL):
		if Yshould[p] == YpredictionConsecutiveSignal4[p]:
			ratio4 += 1
		else:
			dicDB[Yshould[p]] += 1
	errors4= ratio4
	ratio4 = float(ratio4)

	ratio4 = ratio4 / len(Yshould)
	print("Similarity percentile : " + str(ratio4))
	print(str(len(Yshould)- errors4) + " errors ( " + str(100-100*float(errors4)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(XconsecutiveSignal[j])) + " training samples (total " + str(len(YconsecutiveSignal)) +" ) : " + str(dicDB))
	#with open("randomForestModel" + str(ID) ,"wb") as f:
		#pickle.dump(clf4, f)
	return clf4, YpredictionConsecutiveSignal4, Yshould


def givesTriList(list):
	res1 = []
	res2 = []
	res3 = []
	res4 = []
	for l in list:
		res1.append([[l[0][0],l[0][1],l[0][2]], l[1]])
		res2.append([[l[0][0],l[0][1], l[0][3]], l[1]])

		res3.append([[l[0][0], l[0][2],l[0][3]], l[1]])
		res4.append([[l[0][1],l[0][2],l[0][3]], l[1]])
	res = [res1, res2, res3, res4]
	return res

def givesList(DB_NAME, BSSID):
	
	FILENAME = DB_NAME[:-3] + ".csv"


	with sqlite3.connect(DB_NAME) as conn:
		c = conn.cursor()
		MAXID = 4

		
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
		extractedSignalsList = []

		for row in rows:
			extractedSignalsList.append([row[0], row[1].encode("ascii"), row[2].encode("ascii"), row[3], row[4]])
	#We have the rssis list by rpis' id : [id, RSSI] -> extractedSignalsList
	TIME_WINDOW = 15


	#index of the extractedSignalsList containing the succesive RSSIs by id : [RSSI1, RSSI2, ... , RSSIIDMAX] -> consecutiveSignalsList
	i = -1



	consecutiveSignalsList = []
	consecutiveSignal = [0]*MAXID
	#Initialisation of the timers for each RPIS : 

	timersBefore = [0]*MAXID

	# initialisation of the timers:
	k = 0
	while 0 in timersBefore:
		timersBefore[extractedSignalsList[k][0] - 1] = extractedSignalsList[k][3]
		k += 1

	timersAfter = [0]*MAXID
	idRPI = extractedSignalsList[0][0] - 1
	#index of extractedSignalsList
	j = 0

	while j < len(extractedSignalsList):
		row = extractedSignalsList[j]
		TIME_STAMP = int(row[3])
		timersAfter[idRPI] = int(row[3])
		idRPI = row[0] - 1

		if isinstance(row[4], numbers.Number) and row[4] < 1:

			#If there have not been an update from all RPIS in the TIME_WINDOW : abandon of current index 
			# One of the RPIS have not manifested himself
			for l in range(MAXID):
				if timersAfter[idRPI] - timersBefore[l] > TIME_WINDOW and l != idRPI:
					consecutiveSignal[l] = 0
					timersBefore[l] = timersAfter[idRPI]

		
			#consecutiveSignal[idRPI] = rssiWithHumidity(timersAfter[idRPI], row[4])
			consecutiveSignal[idRPI] = row[4]

			if not 0 in consecutiveSignal and (len(consecutiveSignalsList) == 0 or (len(consecutiveSignalsList) > 0 and consecutiveSignal != consecutiveSignalsList[-1])): 
				roundedSignal = [0]*MAXID
				for m in range(MAXID):
					roundedSignal[m] = int(10 * consecutiveSignal[m]) / 10.0
				consecutiveSignalsList.append([roundedSignal, TIME_STAMP])

				i += 1
			timersBefore[idRPI] = timersAfter[idRPI]

		j+=1
	lengthAfter = len(consecutiveSignalsList)

	#Debut du test de consecutiveSignalaison
	ultiList = []
	for p in range(len(consecutiveSignalsList) - 1):
		extractedSignalsList1 = consecutiveSignalsList[p]
		extractedSignalsList2 = consecutiveSignalsList[p+1]
		consecutiveSignal = []
		i = 0
		MAX = len(extractedSignalsList1[0])
		oneCombinaison = [[0]*4, 500]
		for z in range(len(extractedSignalsList1[0])):
			for e in range(len(extractedSignalsList1[0])):
				for r in range(len(extractedSignalsList1[0])):
					oneCombinaison[0] = [elem for elem in extractedSignalsList1[0]]
					oneCombinaison[0][z] = extractedSignalsList2[0][z]
					oneCombinaison[0][e] = extractedSignalsList2[0][e]
					oneCombinaison[0][r] = extractedSignalsList2[0][r]
					oneCombinaison[1] = extractedSignalsList1[1]
					if not oneCombinaison in consecutiveSignal:
						consecutiveSignal.append(oneCombinaison)

		consecutiveSignal.insert(0, extractedSignalsList2)
		consecutiveSignal.insert(0, extractedSignalsList1)
		
		ultiList.extend(consecutiveSignal)
	return [ultiList, givesTriList(ultiList), consecutiveSignalsList, givesTriList(consecutiveSignalsList)]

XconsecutiveSignalCombinaisons = []
XconsecutiveSignalCombinaisons1 = []
XconsecutiveSignalCombinaisons2 = []
XconsecutiveSignalCombinaisons3 = []
XconsecutiveSignalCombinaisons4 = []
YconsecutiveSignalCombinaisons = []

XconsecutiveSignal = []
XconsecutiveSignal1 = []
XconsecutiveSignal2 = []
XconsecutiveSignal3 = []
XconsecutiveSignal4 = []
YconsecutiveSignal = []
# CHANGE DB NAMES HERE
DB_NAME = "MONDAYWEEK4AFTERNOON"

DBS = [[DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"], [DB_NAME, "F2:39:F2:6A:80:89", "fenetre_russia"], [DB_NAME, "C7:62:97:12:1E:35", "the"], [DB_NAME, "E4:FA:6E:AF:58:19", "carte_bancaire"]]
for name in DBS:
	bigList = givesList(name[0]+".db", name[1])

	extractedSignalsList4 ,extractedSignalsList3_1, extractedSignalsList3_2, extractedSignalsList3_3, extractedSignalsList3_4= bigList[0], bigList[1][0], bigList[1][1], bigList[1][2], bigList[1][3], 
	XconsecutiveSignalCombinaisons.extend(extractedSignalsList4)
	XconsecutiveSignalCombinaisons1.extend(extractedSignalsList3_1)
	XconsecutiveSignalCombinaisons2.extend(extractedSignalsList3_2)
	XconsecutiveSignalCombinaisons3.extend(extractedSignalsList3_3)
	XconsecutiveSignalCombinaisons4.extend(extractedSignalsList3_4)
	YconsecutiveSignalCombinaisons.extend([name[2]]*len(extractedSignalsList4))	
	
	extractedSignalsListfinal4 ,extractedSignalsListfinal3_1, extractedSignalsListfinal3_2, extractedSignalsListfinal3_3, extractedSignalsListfinal3_4= bigList[2], bigList[3][0], bigList[3][1], bigList[3][2], bigList[3][3], 

	XconsecutiveSignal.extend(extractedSignalsListfinal4)
	XconsecutiveSignal1.extend(extractedSignalsListfinal3_1)
	XconsecutiveSignal2.extend(extractedSignalsListfinal3_2)
	XconsecutiveSignal3.extend(extractedSignalsListfinal3_3)
	XconsecutiveSignal4.extend(extractedSignalsListfinal3_4)
	YconsecutiveSignal.extend([name[2]]*len(extractedSignalsListfinal4))	

#Preparation des Y:
#Add timestamps to Y lists 
#sort all lists by timestamps (without the timestamps)
#Should be good

YconsecutiveSignalCombinaisonsTemp = []
YconsecutiveSignalTemp = []
for d in range(len(YconsecutiveSignalCombinaisons)):
	YconsecutiveSignalCombinaisonsTemp.append([YconsecutiveSignalCombinaisons[d], XconsecutiveSignalCombinaisons[d][1]])
for d in range(len(YconsecutiveSignal)):
	YconsecutiveSignalTemp.append([YconsecutiveSignal[d], XconsecutiveSignal[d][1]])

XconsecutiveSignalCombinaisons.sort(key=lambda x: x[1])
XconsecutiveSignalCombinaisons1.sort(key=lambda x: x[1])
XconsecutiveSignalCombinaisons2.sort(key=lambda x: x[1])
XconsecutiveSignalCombinaisons3.sort(key=lambda x: x[1])
XconsecutiveSignalCombinaisons4.sort(key=lambda x: x[1])
XconsecutiveSignal.sort(key=lambda x: x[1])
XconsecutiveSignal1.sort(key=lambda x: x[1])
XconsecutiveSignal2.sort(key=lambda x: x[1])
XconsecutiveSignal3.sort(key=lambda x: x[1])
XconsecutiveSignal4.sort(key=lambda x: x[1])
YconsecutiveSignalCombinaisonsTemp.sort(key=lambda x: x[1])
YconsecutiveSignalTemp.sort(key=lambda x: x[1])


graph = []
graph1 = []
graph2 = []
graph3 = []
graph4 = []
per = []
for minutes in [x for x in range(1,150)]:
	print("minutes: " + str(minutes))
	meanLocale = 0
	meanLocale1 = 0
	meanLocale2 = 0
	meanLocale3 = 0
	meanLocale4 = 0
	XpartialC = timeseparation(XconsecutiveSignalCombinaisons, minutes)
	Xpartial1C = timeseparation(XconsecutiveSignalCombinaisons1, minutes)
	Xpartial2C = timeseparation(XconsecutiveSignalCombinaisons2, minutes)
	Xpartial3C = timeseparation(XconsecutiveSignalCombinaisons3, minutes)
	Xpartial4C = timeseparation(XconsecutiveSignalCombinaisons4, minutes)
	Xpartial = timeseparation(XconsecutiveSignal, minutes)
	Xpartial1 = timeseparation(XconsecutiveSignal1, minutes)
	Xpartial2 = timeseparation(XconsecutiveSignal2, minutes)
	Xpartial3 = timeseparation(XconsecutiveSignal3, minutes)
	Xpartial4 = timeseparation(XconsecutiveSignal4, minutes)
	YpartialC = timeseparation(YconsecutiveSignalCombinaisonsTemp, minutes)
	Ypartial = timeseparation(YconsecutiveSignalTemp, minutes)
	if len(Xpartial) > 2:
		for j in range(len(Xpartial) - 2):

			sizeTest = 1
			clf3_1, YpredictionConsecutiveSignal3_1, Yshould  = givesClassifier("3_1", DBS, Xpartial1C, Xpartial1, YpartialC, Ypartial, sizeTest, j)
			clf3_2, YpredictionConsecutiveSignal3_2, Yshould  = givesClassifier("3_2", DBS, Xpartial2C, Xpartial2, YpartialC, Ypartial, sizeTest, j)
			clf3_3, YpredictionConsecutiveSignal3_3, Yshould  = givesClassifier("3_3", DBS, Xpartial3C, Xpartial3, YpartialC, Ypartial, sizeTest, j)
			clf3_4, YpredictionConsecutiveSignal3_4, Yshould  = givesClassifier("3_4", DBS, Xpartial4C, Xpartial4, YpartialC, Ypartial, sizeTest, j)
			clf4, YpredictionConsecutiveSignal4, Yshould = givesClassifier("4", DBS, XpartialC, Xpartial, YpartialC, Ypartial, sizeTest, j)
			Yshould = givesYshould(Ypartial, j+1)

			YpredictionConsecutiveSignal4 = clf4.predict(Xpartial[j + 1])
			print("FINAL RESULTS")

			ratio = 0
			rangeL = len(YpredictionConsecutiveSignal4)
			if rangeL > len(Yshould):
				rangeL = len(Yshould)


			for k in range(rangeL):
				proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
				pos = str(YpredictionConsecutiveSignal4[k])
				if pos == Yshould[k]:
					ratio += 1
			errors = ratio
			ratio = float(ratio)
			ratio = ratio / len(Yshould)
			meanLocale += ratio

			#print("Similarity percentile : " + str(ratio))
			#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
			print("Ratio with only 4model " + str((1-ratio)*100))
			YpredictionConsecutiveSignal4 = clf4.predict(Xpartial[j + 1])
			YpredictionConsecutiveSignal3_1 = clf3_1.predict(Xpartial1[j + 1])
			YpredictionConsecutiveSignal3_2 = clf3_2.predict(Xpartial2[j + 1])
			YpredictionConsecutiveSignal3_3 = clf3_3.predict(Xpartial3[j + 1])
			YpredictionConsecutiveSignal3_4 = clf3_4.predict(Xpartial4[j + 1])

		 	ratio = 0
			rangeL = len(YpredictionConsecutiveSignal4)
			if rangeL > len(Yshould):
				rangeL = len(Yshould)


			for k in range(rangeL):
				proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
				pos4 = str(YpredictionConsecutiveSignal4[k])
				pos3_1 = str(YpredictionConsecutiveSignal3_1[k])
				pos3_2 = str(YpredictionConsecutiveSignal3_2[k])
				pos3_3 = str(YpredictionConsecutiveSignal3_3[k])
				pos3_4 = str(YpredictionConsecutiveSignal3_4[k])
				proba[pos4] += 0
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
			meanLocale1 += ratio

			#print("Similarity percentile : " + str(ratio))
			#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
			print("Ratio with 4model vote at 0 " + str((1-ratio)*100))

			#TODO : AVANT L'ENTRAINEMENT ORDONNER LES LISTES Xpartial et Ypartial PAR TIMESTAMP PLUTOT QUE PAR PLACES -> ENFER MAIS IL FAUT BIEN
			#		LA SUITE DU CODE LOL



			ratio = 0
			rangeL = len(YpredictionConsecutiveSignal4)
			if rangeL > len(Yshould):
				rangeL = len(Yshould)


			for k in range(rangeL):
				proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
				pos4 = str(YpredictionConsecutiveSignal4[k])
				pos3_1 = str(YpredictionConsecutiveSignal3_1[k])
				pos3_2 = str(YpredictionConsecutiveSignal3_2[k])
				pos3_3 = str(YpredictionConsecutiveSignal3_3[k])
				pos3_4 = str(YpredictionConsecutiveSignal3_4[k])
				proba[pos4] += 1
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
			meanLocale2 += ratio

			#print("Similarity percentile : " + str(ratio))
			#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
			print("Ratio with 4model vote at 1"  + " " + str((1-ratio)*100))

			#TODO : AVANT L'ENTRAINEMENT ORDONNER LES LISTES Xpartial et Ypartial PAR TIMESTAMP PLUTOT QUE PAR PLACES -> ENFER MAIS IL FAUT BIEN
			#		LA SUITE DU CODE LOL



			YpredictionConsecutiveSignal = probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3, clf3_3, Xpartial, Xpartial1, Xpartial2, Xpartial3, Xpartial4, j+1)
		 	ratio = 0

			rangeL = len(YpredictionConsecutiveSignal)
			if rangeL > len(Yshould):
				rangeL = len(Yshould)


			for k in range(rangeL):
				if YpredictionConsecutiveSignal[k] == Yshould[k]:
					ratio += 1
			errors = ratio
			ratio = float(ratio)
			ratio = ratio / len(Yshould)
			meanLocale3 += ratio

				#print("Similarity percentile : " + str(ratio))
				#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
			print("Ratio M + S proba " + str((1-ratio)*100))
			
			YpredictionConsecutiveSignal = probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_3, Xpartial1, Xpartial2, Xpartial3, Xpartial4, j+1)
		 	ratio = 0

			rangeL = len(YpredictionConsecutiveSignal)
			if rangeL > len(Yshould):
				rangeL = len(Yshould)


			for k in range(rangeL):
				if YpredictionConsecutiveSignal[k] == Yshould[k]:
					ratio += 1
			errors = ratio
			ratio = float(ratio)
			ratio = ratio / len(Yshould)
			meanLocale4 += ratio
				#print("Similarity percentile : " + str(ratio))
				#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
			print("Ratio proba S " + str((1-ratio)*100))
		if len(Xpartial) - 2 != 0:
			print(len(per))
			print(len(graph4))
			per.append(minutes)

			graph4.append(100-100*float(meanLocale4)/(len(Xpartial) - 2))
			graph.append(100-100*float(meanLocale)/(len(Xpartial) - 2))
			graph1.append(100-100*float(meanLocale1)/(len(Xpartial) - 2))
			graph2.append(100-100*float(meanLocale2)/(len(Xpartial) - 2))
			graph3.append(100-100*float(meanLocale3)/(len(Xpartial) - 2))

plt.gca().set_color_cycle(['red', 'green', 'blue', 'black', 'orange'])
axes = plt.gca()
axes.set_ylim([0,45])
plt.plot(per,graph)
plt.plot(per,graph1)
plt.plot(per,graph2)
plt.plot(per,graph3)
plt.plot(per,graph4)

plt.ylabel('% of errors on prediction sample')
plt.xlabel('training interval (minutes)')
fontP = FontProperties()
fontP.set_size('small')
plt.legend(['Main model only', 'Submodels (deterministic)', 'Main + Submodels (deterministic)', 'Submodels (probabilistic)', 'Main + Submodels (probabilistic)'], prop = fontP)

plt.show()