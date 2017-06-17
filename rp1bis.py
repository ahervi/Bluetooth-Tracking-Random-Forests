import paho.mqtt.client as mqtt
import sqlite3
import time

def on_publish(client, userdata, result):
	print("message sent")
	pass


mqttc = mqtt.Client()
mqttc.on_publish = on_publish
mqttc.connect("192.168.43.143", 1883)
IDPI = 1
while True:
        with open("./blue_hydra/blue_hydra_rssi.log", "rb") as f:
              found = false
              for line in f:
              	  bssid = line[14:31]
                  timeStamp = line[:10]
                  if last_bssid == bssid and last_timeStamp == timeStamp:
                  	  found = true
                  if found:
                      rssi = line[-4:]
                      message = IDPI + "," + str(timeStamp) + "," + rssi
                      print(message)

                  	  mqttc.publish("rpis", message)
                      last_bssid = bssid
                      last_timeStamp = timeStamp

        found = false
        time.sleep(1)
