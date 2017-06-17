import sqlite3
import os

exist = true
if not os.path.exists('combined.db'): 
	exist = false

conn = sqlite3.connect("combined.db")

c = conn.cursor()
if not exist:
	c.execute('''
    	CREATE TABLE COMBINED(ID INTEGER PRIMARY KEY, BSSID TEXT, TIME_STAMP INTEGER
                       RSSI INTEGER)
	''')

ID1 = liste[0]
BSSID1 = liste[1]
TIME_STAMP1 = liste[2]
RSSI1 = liste[3]

c.execute('''INSERT INTO COMBINED(ID, BSSID, TIME_STAMP, RSSI)
                  VALUES(?,?,?,?)''', (ID1,BSSID1, TIME_STAMP1, RSSI1))

conn.commit()