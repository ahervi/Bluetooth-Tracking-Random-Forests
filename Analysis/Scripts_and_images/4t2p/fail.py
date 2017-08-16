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
def timeseparation(XconsecutiveSignalCombinaisons, seconds):
	bufferRSSIS = []
	newXconsecutiveSignalCombinaisons = []
	oldTime = XconsecutiveSignalCombinaisons[0][1]
	for v in range(len(XconsecutiveSignalCombinaisons)):

		if XconsecutiveSignalCombinaisons[v][1] - oldTime > seconds:
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

def givesClassifier(ID, DBS,Xpred, Ypred, XconsecutiveSignal, YconsecutiveSignal, sizeTest):
	limitTestSampleCombi = int(math.floor(int(len(XconsecutiveSignal)*sizeTest)))
	clf4 = RandomForestClassifier(n_estimators=100)
	clf4 = clf4.fit(XconsecutiveSignal[:limitTestSampleCombi], YconsecutiveSignal[:limitTestSampleCombi])

	YpredictionConsecutiveSignal4 = clf4.predict(Xpred)
	Yshould = Ypred
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
	print(str(len(Yshould)- errors4) + " errors ( " + str(100-100*float(errors4)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(XconsecutiveSignal)) + " training samples (total " + str(len(YconsecutiveSignal)) +" ) : " + str(dicDB))
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


	return [consecutiveSignalsList, givesTriList(consecutiveSignalsList)]

XconsecutiveSignal = []
XconsecutiveSignal1 = []
XconsecutiveSignal2 = []
XconsecutiveSignal3 = []
XconsecutiveSignal4 = []
YconsecutiveSignal = []
Ypred = []
Xpred = []
Xpred1 = []
Xpred2 = []
Xpred3 = []
Xpred4 = []
# CHANGE DB NAMES HERE

DB_NAME = "4t2pV2"

DBS_PRED= [[DB_NAME, "F2:39:F2:6A:80:89", "me"], [DB_NAME, "C7:62:97:12:1E:35", "russia"]]
DBS = [[DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"], [DB_NAME, "E4:FA:6E:AF:58:19", "carte_bancaire"]]

for name in DBS:
	bigList = givesList(name[0]+".db", name[1])


	extractedSignalsListfinal4 ,extractedSignalsListfinal3_1, extractedSignalsListfinal3_2, extractedSignalsListfinal3_3, extractedSignalsListfinal3_4= bigList[0], bigList[1][0], bigList[1][1], bigList[1][2], bigList[1][3], 

	XconsecutiveSignal.extend(extractedSignalsListfinal4)
	XconsecutiveSignal1.extend(extractedSignalsListfinal3_1)
	XconsecutiveSignal2.extend(extractedSignalsListfinal3_2)
	XconsecutiveSignal3.extend(extractedSignalsListfinal3_3)
	XconsecutiveSignal4.extend(extractedSignalsListfinal3_4)
	YconsecutiveSignal.extend([name[2]]*len(extractedSignalsListfinal4))	

for name in DBS_PRED:
	bigListPred = givesList(name[0]+".db", name[1])


	extractedSignalsListfinalPred4 ,extractedSignalsListfinalPred3_1, extractedSignalsListfinalPred3_2, extractedSignalsListfinalPred3_3, extractedSignalsListfinalPred3_4 = bigListPred[0], bigListPred[1][0], bigListPred[1][1], bigListPred[1][2], bigListPred[1][3]
	Xpred.extend(extractedSignalsListfinalPred4)
	Xpred1.extend(extractedSignalsListfinalPred3_1)
	Xpred2.extend(extractedSignalsListfinalPred3_2)
	Xpred3.extend(extractedSignalsListfinalPred3_3)
	Xpred4.extend(extractedSignalsListfinalPred3_4)
	Ypred.extend([name[2]]*len(extractedSignalsListfinalPred4))		



	
#Preparation des Y:
#Add timestamps to Y lists 
#sort all lists by timestamps (without the timestamps)
#Should be good

YpredTemp = []
YconsecutiveSignalTemp = []
for d in range(len(Ypred)):
	YpredTemp.append([Ypred[d], Xpred[d][1]])
for d in range(len(YconsecutiveSignal)):
	YconsecutiveSignalTemp.append([YconsecutiveSignal[d], XconsecutiveSignal[d][1]])


XconsecutiveSignal.sort(key=lambda x: x[1])

Xpred.sort(key=lambda x: x[1])
YpredTemp.sort(key=lambda x: x[1])
YconsecutiveSignalTemp.sort(key=lambda x: x[1])

XconsecutiveSignal = [x[0] for x in XconsecutiveSignal]
Xpred = [x[0] for x in Xpred]
YpredTemp = [x[0] for x in YpredTemp]
YconsecutiveSignalTemp = [x[0] for x in YconsecutiveSignalTemp]
graph = []

per = []


for i in range(1,100):
	sizeTest = 0.00999*i
	Yshould = Ypred


			
	clf4, YpredictionConsecutiveSignal4, Yshould = givesClassifier("4", DBS,Xpred, YpredTemp, XconsecutiveSignal, YconsecutiveSignal, sizeTest)
	Yshould = YpredTemp
	YpredictionConsecutiveSignal4 = clf4.predict(Xpred)
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
	meanLocale = ratio

	#print("Similarity percentile : " + str(ratio))
	#print(str(len(Yshould)- errors) + " errors ( " + str(100-100*float(errors)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(X[:limitTestSample])) + " training samples (total " + str(len(Y)) +" ) : " + str(dicDB))
	print("Ratio with only 4model " + str((1-ratio)*100))


	per.append(sizeTest*100)

	graph.append(100-100*float(errors)/len(Yshould))
		
plt.gca().set_color_cycle(['black', 'green', 'blue', 'red', 'orange'])
axes = plt.gca()
#axes.set_ylim([0,45])
plt.plot(per,graph)

plt.ylabel('% of errors on prediction sample')
plt.xlabel('% of training dataset')
fontP = FontProperties()
fontP.set_size('small')
plt.legend(['Main model only'], prop = fontP)

plt.show()