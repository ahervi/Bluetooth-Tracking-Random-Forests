import paho.mqtt.client as mqtt
import sqlite3
import os

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("rpis")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    liste = msg.payload.split(",")
    print(msg.topic+" "+str(liste))
    exist = True
    if not os.path.exists('combined.db'):
        exist = False

    conn = sqlite3.connect("combined.db")

    c = conn.cursor()
    if not exist:
	c.execute('''
    	CREATE TABLE COMBINED(ID INTEGER, BSSID TEXT, NAME TEXT, TIME_STAMP INTEGER,
                       RSSI INTEGER)
	''')

    ID1 = liste[0]
    BSSID1 = liste[1]
    NAME1 = liste[2]
    TIME_STAMP1 = liste[3]
    RSSI1 = liste[4]

    c.execute('''INSERT INTO COMBINED(ID, BSSID, NAME, TIME_STAMP, RSSI)
                  VALUES(?,?,?,?,?)''', (ID1,BSSID1, NAME1, TIME_STAMP1, RSSI1))

    conn.commit()



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.43.143", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
