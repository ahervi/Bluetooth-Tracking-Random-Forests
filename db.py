import sqlite3
import os

exist = true
if not os.path.exists('combined.db'): 
	exist = false

conn = sqlite3.connect("combined.db")

c = conn.cursor()
if not exist:
	c.execute('''
    	CREATE TABLE COMBINED(ID INTEGER PRIMARY KEY, BSSID TEXT,
                       RSSI INTEGER)
	''')

ID1 = liste[0]
BSSID1 = liste[1]
RSSI1 = liste[2]

c.execute('''INSERT INTO COMBINED(ID, BSSID, RSSI)
                  VALUES(?,?,?,?)''', (ID1,BSSID1, RSSI1))

conn.commit()