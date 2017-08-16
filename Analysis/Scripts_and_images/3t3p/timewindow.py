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
	
def givesClassifier(ID, DBS, XconsecutiveSignal, YconsecutiveSignal, Xpred, Ypred):
	clf4 = RandomForestClassifier(n_estimators=100)

	clf4 = clf4.fit(XconsecutiveSignal, YconsecutiveSignal)


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
	print("size "  + str(len(Yshould)- errors4) + " errors ( " + str(100-100*float(errors4)/len(Yshould))+ "% ) on " + str(len(Yshould)) + " predicted samples out of " + str(len(XconsecutiveSignal)) + " training samples : " + str(dicDB))
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

def givesList(DB_NAME, BSSID, size, TIME_WINDOW):
	
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
	
	graph = []
	per = []
	
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

DBS_PRED= [[DB_NAME, "F2:39:F2:6A:80:89", "me"], [DB_NAME, "C7:62:97:12:1E:35", "russia"], [DB_NAME, "E4:FA:6E:AF:58:19", "fenetre_casque"]]
DBS = [[DB_NAME, "C1:CF:31:F3:29:6C", "russia"], [DB_NAME, "C7:64:6C:03:B9:40", "me"], [DB_NAME, "DA:E7:8C:CA:05:CF", "fenetre_casque"]]
XuntouchedF4 = []

# CHANGE DB NAMES HERE

graph1 = []
graph2 = []
graph3 = []
graph4 = []
graph = []
per = []
size = 0.98

for TIME_WINDOW in [float(x)/100 for x in range(1,2400)]:
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
		bigList = givesList(name[0]+".db", name[1], size, TIME_WINDOW)


		extractedSignalsListfinal4 ,extractedSignalsListfinal3_1, extractedSignalsListfinal3_2, extractedSignalsListfinal3_3, extractedSignalsListfinal3_4= bigList[0], bigList[1][0], bigList[1][1], bigList[1][2], bigList[1][3]
		XconsecutiveSignal.extend(extractedSignalsListfinal4)
		XconsecutiveSignal1.extend(extractedSignalsListfinal3_1)
		XconsecutiveSignal2.extend(extractedSignalsListfinal3_2)
		XconsecutiveSignal3.extend(extractedSignalsListfinal3_3)
		XconsecutiveSignal4.extend(extractedSignalsListfinal3_4)
		YconsecutiveSignal.extend([name[2]]*len(extractedSignalsListfinal4))		
	for name in DBS_PRED:
		bigListPred = givesList(name[0]+".db", name[1],0, TIME_WINDOW)


		extractedSignalsListfinalPred4 ,extractedSignalsListfinalPred3_1, extractedSignalsListfinalPred3_2, extractedSignalsListfinalPred3_3, extractedSignalsListfinalPred3_4 = bigListPred[0], bigListPred[1][0], bigListPred[1][1], bigListPred[1][2], bigListPred[1][3]
		Xpred.extend(extractedSignalsListfinalPred4)
		Xpred1.extend(extractedSignalsListfinalPred3_1)
		Xpred2.extend(extractedSignalsListfinalPred3_2)
		Xpred3.extend(extractedSignalsListfinalPred3_3)
		Xpred4.extend(extractedSignalsListfinalPred3_4)
		Ypred.extend([name[2]]*len(extractedSignalsListfinalPred4))		
	length1 = 100
	sizeX = 0.009*len(XconsecutiveSignal)
	XconsecutiveSignal = [XconsecutiveSignal[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	XconsecutiveSignal1 = [XconsecutiveSignal1[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	XconsecutiveSignal2 = [XconsecutiveSignal2[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	XconsecutiveSignal3 = [XconsecutiveSignal3[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	XconsecutiveSignal4 = [XconsecutiveSignal4[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	YconsecutiveSignal = [YconsecutiveSignal[int(i*sizeX):int((i+1)*sizeX)] for i in range(0,length1)]
	#sizeXP = 0.09*len(Xpred)
	# Xpred = [Xpred[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	# Xpred1 = [Xpred1[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	# Xpred2 = [Xpred2[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	# Xpred3 = [Xpred3[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	# Xpred4 = [Xpred4[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	# Ypred = [Ypred[int(i*sizeXP):int((i+1)*sizeXP)] for i in range(0,100)]
	Xt = []
	Yt = []
	Xt1 = []
	Xt2 = []
	Xt3 = []
	Xt4 = []
	for i in range(1,length1):
		Xt.extend(XconsecutiveSignal[i])
		Xt1.extend(XconsecutiveSignal1[i])
		Xt2.extend(XconsecutiveSignal2[i])
		Xt3.extend(XconsecutiveSignal3[i])
		Xt4.extend(XconsecutiveSignal4[i])
		Yt.extend(YconsecutiveSignal[i])
	per.append(TIME_WINDOW*100/60)
	Yshould = Ypred
	clf4, YpredictionConsecutiveSignal4 = givesClassifier("4", DBS, Xt, Yt, Xpred, Ypred)
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

plt.gca().set_color_cycle(['black', 'green', 'blue', 'red', 'orange'])
axes = plt.gca()
axes.set_ylim([0,45])
plt.plot(per,graph)
#plt.plot(per,graph1)
#plt.plot(per,graph2)
#plt.plot(per,graph3)
#plt.plot(per,graph4)

#plt.legend(['Main model only', 'Submodels (deterministic)', 'Main + Submodels (deterministic)', 'Submodels (probabilistic)', 'Main + Submodels (probabilistic)'], loc='upper right')
plt.legend(['Main model'], loc='upper right')
plt.ylabel('% of errors on prediction sample')
plt.xlabel('time for signal reception (minutes)')
plt.show()
