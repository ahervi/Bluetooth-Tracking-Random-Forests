import paho.mqtt.client as mqtt
import sqlite3
import os
import pickle
import numbers 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time 
import operator

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


    TIME_WINDOW = 15



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
        if BSSID1 == "F2:39:F2:6A:80:89":
            print("Seen by "+ str(ID1))

            if OLDTIME[ID1 - 1] == 0:
                OLDTIME[ID1 - 1] = NEWTIME[ID1 - 1]

            for l in range(MAXID):
                if (NEWTIME[ID1 - 1] - OLDTIME[l - 1]) > TIME_WINDOW and l != ID1:  
                    RSSIS[l - 1] = 0
                    OLDTIME[l - 1] = NEWTIME[ID1 - 1]
           
            if (NEWTIME[ID1 - 1] - OLDTIME[ID1 - 1]) > TIME_WINDOW :
                RSSIS[ID1] = RSSI1   

               

              


            else:
                
                RSSI1 = int(RSSI1)
                RSSIS[ID1 - 1] = RSSI1
                print(RSSIS)
            if not 0 in RSSIS:
                
                with open("positions","r") as f:
                    positions = pickle.load(f)

                with open("proba","r") as f:
                    proba = pickle.load(f)


                RANGE = 10
                for i in range(RANGE):
                    with open("randomForestModel"+str(i),"r") as f:
                        randomForestModel = pickle.load(f)

                    POS = randomForestModel.predict([RSSIS])
                    pos = str(POS[0])
                    proba[pos] += 1
                print(str(proba))
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
