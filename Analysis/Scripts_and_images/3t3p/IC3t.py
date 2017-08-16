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
import scipy as sp
import scipy.stats
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h
#size test does not vary with size
def rssiWithHumidity(timestamp, rssi):
	res = math.cos((2*math.pi*float(timestamp2hour(timestamp))-1)/24)
	if res < -0.5:		
		res = -0.5
	return rssi - res
def timestamp2hour(timestamp):
	return int(datetime.datetime.fromtimestamp(int(timestamp)).strftime('%H'))

def probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3,clf3_4, X, X1, X2, X3, X4, Xpred, Xpred1, Xpred2, Xpred3, Xpred4):
	YpredictionConsecutiveSignal = []
	probas3_1 = clf3_1.predict_proba(Xpred1)
	probas3_2 = clf3_2.predict_proba(Xpred2)
	probas3_3 = clf3_3.predict_proba(Xpred3)
	probas3_4 = clf3_4.predict_proba(Xpred4)

	probas4 = clf4.predict_proba(Xpred)

	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas4[i][j]+probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal

def probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_4, X1, X2, X3, X4, Xpred1, Xpred2, Xpred3, Xpred4):
	YpredictionConsecutiveSignal = []
	probas3_1 = clf3_1.predict_proba(Xpred1)
	probas3_2 = clf3_2.predict_proba(Xpred2)
	probas3_3 = clf3_3.predict_proba(Xpred3)
	probas3_4 = clf3_4.predict_proba(Xpred4)
	places = ['carte_bancaire', 'fenetre_casque', 'fenetre_russia', 'me', 'russia', 'the']

	for i in range(len(probas3_1)):

		probas = [probas3_1[i][j]+probas3_2[i][j]+probas3_3[i][j]+probas3_4[i][j] for j in range(len(probas3_1[i]))]
		maxIndex = max(enumerate(probas),key=lambda x: x[1])[0]
		YpredictionConsecutiveSignal.append(places[maxIndex])

	return YpredictionConsecutiveSignal
	
def givesClassifier(ID, DBS, XconsecutiveSignal, YconsecutiveSignal, sizeTest, Xpred, Ypred):
	clf4 = RandomForestClassifier(n_estimators=100)

	limitTestSampleCombi = int(math.floor(int(len(XconsecutiveSignal)*sizeTest)))
	clf4 = clf4.fit(XconsecutiveSignal[:limitTestSampleCombi], YconsecutiveSignal[:limitTestSampleCombi])


	YpredictionConsecutiveSignal4 = clf4.predict(Xpred)
	Yshould = Ypred
	ratio4 = 0
	dicDB = dict()
	for db in DBS:
		dicDB[db[2]] = 0

	for j in range(len(YpredictionConsecutiveSignal4)):
		if Yshould[j] == YpredictionConsecutiveSignal4[j]:
			ratio4 += 1
		else:
			dicDB[YpredictionConsecutiveSignal4[j]] += 1
	errors4= ratio4
	ratio4 = float(ratio4)

	ratio4 = ratio4 / len(Yshould)
	print("Similarity percentile : " + str(ratio4))
	print("size " + str(sizeTest) + str(len(Yshould)- errors4) + " errors ( " + str(100-100*float(errors4)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(XconsecutiveSignal)) + " training samples : " + str(dicDB))
	#with open("randomForestModel" + str(ID) ,"wb") as f:
		#pickle.dump(clf4, f)
	return clf4, YpredictionConsecutiveSignal4

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

def givesList(DB_NAME, BSSID, size):
	
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
				consecutiveSignalsList.append(roundedSignal)
				i += 1
			timersBefore[idRPI] = timersAfter[idRPI]

		j+=1
	lengthAfter = len(consecutiveSignalsList)
	#trying
	random.seed(1)
	b = range(len(consecutiveSignalsList))
	random.shuffle(b)
	consecutiveSignalsList = [consecutiveSignalsList[i] for i in b] # or:

	if size != 0:
		sizeUntouched = size
		lengthUntouched = int(math.floor(sizeUntouched*len(consecutiveSignalsList)))
		consecutiveSignalsList = consecutiveSignalsList[:lengthUntouched]
		
	return [consecutiveSignalsList, givesTriList(consecutiveSignalsList)]



DB_NAME = "3t3pV2"

DBS_PRED= [[DB_NAME, "F2:39:F2:6A:80:89", "me"]]
DBS = [[DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"]]
XuntouchedF4 = []

# CHANGE DB NAMES HERE

graph = []
per = []
graph1 = []
graph2 = []
graph3 = []
graph4 = []

size = 0.98
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
Ypred = []
Xpred = []
Xpred1 = []
Xpred2 = []
Xpred3 = []
Xpred4 = []

for name in DBS:
	bigList = givesList(name[0]+".db", name[1], size)


	extractedSignalsListfinal4 ,extractedSignalsListfinal3_1, extractedSignalsListfinal3_2, extractedSignalsListfinal3_3, extractedSignalsListfinal3_4= bigList[0], bigList[1][0], bigList[1][1], bigList[1][2], bigList[1][3]
	XconsecutiveSignal.extend(extractedSignalsListfinal4)
	XconsecutiveSignal1.extend(extractedSignalsListfinal3_1)
	XconsecutiveSignal2.extend(extractedSignalsListfinal3_2)
	XconsecutiveSignal3.extend(extractedSignalsListfinal3_3)
	XconsecutiveSignal4.extend(extractedSignalsListfinal3_4)
	YconsecutiveSignal.extend([name[2]]*len(extractedSignalsListfinal4))		
for name in DBS_PRED:
	bigListPred = givesList(name[0]+".db", name[1],0)


	extractedSignalsListfinalPred4 ,extractedSignalsListfinalPred3_1, extractedSignalsListfinalPred3_2, extractedSignalsListfinalPred3_3, extractedSignalsListfinalPred3_4 = bigListPred[0], bigListPred[1][0], bigListPred[1][1], bigListPred[1][2], bigListPred[1][3]
	Xpred.extend(extractedSignalsListfinalPred4)
	Xpred1.extend(extractedSignalsListfinalPred3_1)
	Xpred2.extend(extractedSignalsListfinalPred3_2)
	Xpred3.extend(extractedSignalsListfinalPred3_3)
	Xpred4.extend(extractedSignalsListfinalPred3_4)
	Ypred.extend([name[2]]*len(extractedSignalsListfinalPred4))		

random.seed(1)

b = range(len(XconsecutiveSignal))

random.shuffle(b)
XconsecutiveSignal = [XconsecutiveSignal[i] for i in b] # or:
XconsecutiveSignal1 = [XconsecutiveSignal1[i] for i in b] # or:
XconsecutiveSignal2 = [XconsecutiveSignal2[i] for i in b] # or:
XconsecutiveSignal3 = [XconsecutiveSignal3[i] for i in b] # or:
XconsecutiveSignal4 = [XconsecutiveSignal4[i] for i in b] # or:

YconsecutiveSignal = [YconsecutiveSignal[i] for i in b] # or:



	
for i in range(1000):
	sizeTest = 0.999
	per.append(sizeTest*100)
	Yshould = Ypred
	clf4, YpredictionConsecutiveSignal4 = givesClassifier("4", DBS, XconsecutiveSignal, YconsecutiveSignal, sizeTest, Xpred, Ypred)
	#clf3_1, YpredictionConsecutiveSignal3_1 = givesClassifier("3_1", DBS,XconsecutiveSignal1, YconsecutiveSignal, sizeTest, Xpred1, Ypred)
	#clf3_2, YpredictionConsecutiveSignal3_2 = givesClassifier("3_2", DBS, XconsecutiveSignal2, YconsecutiveSignal, sizeTest, Xpred2, Ypred)
	#clf3_3, YpredictionConsecutiveSignal3_3 = givesClassifier("3_3", DBS, XconsecutiveSignal3, YconsecutiveSignal, sizeTest, Xpred3, Ypred)
	#clf3_4, YpredictionConsecutiveSignal3_4 = givesClassifier("3_4", DBS, XconsecutiveSignal4, YconsecutiveSignal, sizeTest, Xpred4, Ypred)



	
 	ratio = 0
	for k in range(len(YpredictionConsecutiveSignal4)):
		proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
		pos4 = str(YpredictionConsecutiveSignal4[k])

		proba[pos4] += 1
		
		pos = max(proba.iteritems(), key=operator.itemgetter(1))[0]
		if pos == Yshould[k]:
			ratio += 1
	errors = ratio
	ratio = float(ratio)
	ratio = ratio / len(Yshould)
	graph.append(100-100*float(errors)/len(Yshould))




	
 # 	ratio = 0
	# for k in range(len(YpredictionConsecutiveSignal4)):
	# 	proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
	# 	pos4 = str(YpredictionConsecutiveSignal4[k])
	# 	pos3_1 = str(YpredictionConsecutiveSignal3_1[k])
	# 	pos3_2 = str(YpredictionConsecutiveSignal3_2[k])
	# 	pos3_3 = str(YpredictionConsecutiveSignal3_3[k])
	# 	pos3_4 = str(YpredictionConsecutiveSignal3_4[k])
	# 	proba[pos4] += 0
	# 	proba[pos3_1] += 1
	# 	proba[pos3_2] += 1
	# 	proba[pos3_3] += 1
	# 	proba[pos3_4] += 1
	# 	pos = max(proba.iteritems(), key=operator.itemgetter(1))[0]
	# 	if pos == Yshould[k]:
	# 		ratio += 1
	# errors = ratio
	# ratio = float(ratio)
	# ratio = ratio / len(Yshould)
	# graph1.append(100-100*float(errors)/len(Yshould))





 # 	ratio = 0
	# for k in range(len(YpredictionConsecutiveSignal4)):
	# 	proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
	# 	pos4 = str(YpredictionConsecutiveSignal4[k])
	# 	pos3_1 = str(YpredictionConsecutiveSignal3_1[k])
	# 	pos3_2 = str(YpredictionConsecutiveSignal3_2[k])
	# 	pos3_3 = str(YpredictionConsecutiveSignal3_3[k])
	# 	pos3_4 = str(YpredictionConsecutiveSignal3_4[k])
	# 	proba[pos4] += 1
	# 	proba[pos3_1] += 1
	# 	proba[pos3_2] += 1
	# 	proba[pos3_3] += 1
	# 	proba[pos3_4] += 1
	# 	pos = max(proba.iteritems(), key=operator.itemgetter(1))[0]
	# 	if pos == Yshould[k]:
	# 		ratio += 1
	# errors = ratio
	# ratio = float(ratio)
	# ratio = ratio / len(Yshould)
	# graph2.append(100-100*float(errors)/len(Yshould))
	

	# YpredictionConsecutiveSignal = probabilityPredictionMainAndSub(sizeTest, clf4, clf3_1, clf3_2, clf3_3, clf3_4, XconsecutiveSignal, XconsecutiveSignal1, XconsecutiveSignal2, XconsecutiveSignal3, XconsecutiveSignal4, Xpred, Xpred1, Xpred2, Xpred3, Xpred4)
 # 	ratio = 0
	# for k in range(len(YpredictionConsecutiveSignal)):

	# 	if YpredictionConsecutiveSignal[k] == Yshould[k]:
	# 		ratio += 1
	# errors = ratio
	# ratio = float(ratio)
	# ratio = ratio / len(Yshould)
	# graph3.append(100-100*float(errors)/len(Yshould))



	# YpredictionConsecutiveSignal = probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_4, XconsecutiveSignal1, XconsecutiveSignal2, XconsecutiveSignal3, XconsecutiveSignal4, Xpred1, Xpred2, Xpred3, Xpred4)
 # 	ratio = 0
	# for k in range(len(YpredictionConsecutiveSignal)):

	# 	if YpredictionConsecutiveSignal[k] == Yshould[k]:
	# 		ratio += 1
	# errors = ratio
	# ratio = float(ratio)
	# ratio = ratio / len(Yshould)
	# graph4.append(100-100*float(errors)/len(Yshould))

print("3t")
print(np.mean(graph))
print(np.std(graph))
print(mean_confidence_interval(graph))
print(mean_confidence_interval(graph, 0.99))
print(mean_confidence_interval(graph, 0.999))
print(mean_confidence_interval(graph, 0.9999))
