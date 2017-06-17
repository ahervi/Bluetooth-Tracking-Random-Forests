import paho.mqtt.client as mqtt
import sqlite3
import time

def on_publish(client, userdata, result):
	print("message sent")
	pass


mqttc = mqtt.Client()
mqttc.on_publish = on_publish
mqttc.connect("192.168.43.143", 1883)

while True:
        with open("./blue_hydra/blue_hydra_rssi.log", "rb") as f:
              i = 0
              last =[0]*20
              for line in f:
                  i = (i + 1) % 20 
                  last[i] = line
                  pass
              timeStamp = 0        
              for line in reversed(last):  
                  bssid = line[14:31]
     
                  if bssid == "F2:39:F2:6A:80:89" and int(line[:10]) > timeStamp:
                     timeStamp = line[:10]
                     rssi = line[-4:]
              message = str(timeStamp) + "," + rssi
              print(message)

              mqttc.publish("rpi1", message)
        time.sleep(10)
