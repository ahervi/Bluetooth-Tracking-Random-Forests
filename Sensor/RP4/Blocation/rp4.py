import paho.mqtt.client as mqtt
import sqlite3
import time
import os

def on_publish(client, userdata, result):
	print("message sent")
	pass


mqttc = mqtt.Client()
mqttc.on_publish = on_publish
mqttc.connect("192.168.43.63", 1883)
IDPI = os.path.basename(__file__)[2]
first = True

while True:
        
        
        with open("./blue_hydra/blue_hydra_rssi.log", "rb") as f:
              
              found = False
              
              for line in f:
                  
              	  bssid = line[14:31]

                  

                  timeStamp = line[:10]
                  
                  if first :
                      last_bssid = bssid
                      last_timeStamp = timeStamp
                      first = False
                  if found:
                      rssi = line[-4:-1]
                      db_filename = "./blue_hydra/blue_hydra.db"

                      with sqlite3.connect(db_filename) as conn:
	                 cursor = conn.cursor()
	                 cursor.execute("""select name from blue_hydra_devices where address = ? LIMIT 1;
                          """, [bssid])
	
	                 row = cursor.fetchall()
	                 name = "None"
	                 if len(row) > 0:
                             name = str(row[0][0])
                      message = str(IDPI) + "," + bssid + "," + name + "," + str(timeStamp) + "," + rssi
                      print(message)

                      mqttc.publish("rpis/" + str(IDPI), message)
                      last_bssid = bssid
                      last_timeStamp = timeStamp
                  if last_bssid == bssid and last_timeStamp == timeStamp:
                  	  found = True
                  

        time.sleep(1)
