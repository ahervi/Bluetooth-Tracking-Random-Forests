import paho.mqtt.client as mqtt
import sqlite3
import os
import pickle
import numbers 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time 
import operator
import math

def givesTriList(list):
    '''Argument: 
        list : list of lists of length 4
    returns a list of all possible ordered combination of the list elements in groups of three, each ordered type of combination is contained within its own list'''
    
    # res1, until res4 are the lists containing the resulting combinations
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


def probabilityPredictionSub(sizeTest, clf3_1, clf3_2, clf3_3, clf3_4, X1, X2, X3, X4):
    '''Arguments:
        sizeTest : float representing the proportion of the samples used for training. 0 for the all of the samples or 0.66 for classic use
        clf3_1, ..., clf3_4 represents the Random Forest models for each group of three RPIs within the group of four
        X1, ..., X4 are the sample of data for each model
    returns void, it just trains the models and save them'''


    YpredictionConsecutiveSignal = []
    limitTestSampleFinal = int(math.floor(int(len(X1)*sizeTest)))
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

DB_NAME = "real.db"
with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""select max(ID)from COMBINED""")
        maxId = c.fetchall()

        for id in maxId:
            MAXID = id[0]
        
RSSIS =[0]*MAXID

img=mpimg.imread('office.jpg')

positions = {'me':[478, 198], 'russia':[252, 292], 'the':[270, 107], 'fenetre_casque':[619, 564], 'fenetre_russia':[351, 549], 'carte_bancaire':[702, 286]}
proba = {'me':0, 'russia':0, 'the':0, 'fenetre_casque':0, 'fenetre_russia':0, 'carte_bancaire':0}
with open("proba","wb") as f:
    pickle.dump(proba, f)

with open("positions","wb") as f:
    pickle.dump(positions, f)

with open("RSSIS","wb") as f:
    pickle.dump(RSSIS, f)

OLDTIME = [0]*MAXID
NEWTIME = [0]*MAXID
with open("OLDTIME","wb") as f:
    pickle.dump(OLDTIME, f)
with open("NEWTIME","wb") as f:
    pickle.dump(NEWTIME, f)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("rpis/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    global fig


    TIME_WINDOW = 120



    with open("OLDTIME","r") as f:
        OLDTIME = pickle.load(f)
    with open("NEWTIME","r") as f:
        NEWTIME = pickle.load(f)
    with open("RSSIS","r") as f:
        RSSIS = pickle.load(f)

    liste = msg.payload.split(",")
    
    ID1 = int(liste[0])
    BSSID1 = liste[1]
    NAME1 = liste[2]
    TIME_STAMP1 = int(liste[3])
    RSSI1 = liste[4]

    NEWTIME[ID1 - 1] = TIME_STAMP1

    positiv = RSSI1[1:]
    if positiv.isdigit():
        if BSSID1 == "DA:E7:8C:CA:05:CF":
            print("Seen by "+ str(ID1))

            if OLDTIME[ID1 - 1] == 0:
                OLDTIME[ID1 - 1] = NEWTIME[ID1 - 1]

            for l in range(MAXID):
                if (NEWTIME[ID1 - 1] - OLDTIME[l - 1]) > TIME_WINDOW and l != ID1:  
                    RSSIS[l - 1] = 0
                    OLDTIME[l - 1] = NEWTIME[ID1 - 1]
           
            if (NEWTIME[ID1 - 1] - OLDTIME[ID1 - 1]) > TIME_WINDOW :
                RSSIS[ID1 - 1] = RSSI1   

               

              


            else:
                
                RSSI1 = int(RSSI1)
                RSSIS[ID1 - 1] = RSSI1
                print(RSSIS)
            if not 0 in RSSIS:
                
                with open("positions","r") as f:
                    positions = pickle.load(f)

                with open("proba","r") as f:
                    proba = pickle.load(f)
                randomForestModels = []
                identifiers = ["4", "3_1", "3_2", "3_3", "3_4"]
                for i in range(len(identifiers)):
                    with open("randomForestModel"+str(identifiers[i]),"r") as f:
                        randomForestModels.append(pickle.load(f))
                    triList = givesTriList([RSSIS])
                   
                YpredictionSignal = probabilityPredictionSub(0, randomForestModels[0], randomForestModels[1], randomForestModels[2], randomForestModels[3], RSSIS, triList[0], triList[1], triList[2])

                pos = str(YpredictionSignal[0])
                proba[pos] += 1
                pos = max(proba.iteritems(), key=operator.itemgetter(1))[0]
                
                print(pos)
               
                plt.close('all')
                fig = plt.figure()
                plt.imshow(img)
                plt.scatter(positions[pos][0], positions[pos][1] , s=500, c='red', marker='o')
                plt.show(block = False)
                
            OLDTIME[ID1 - 1] = NEWTIME[ID1 - 1]
            with open("OLDTIME","wb") as f:
                pickle.dump(OLDTIME, f)
            with open("NEWTIME","wb") as f:
                pickle.dump(NEWTIME, f)
            with open("RSSIS","wb") as f:
                pickle.dump(RSSIS, f)



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.43.63", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
