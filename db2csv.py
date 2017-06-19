import csv
import sqlite3

with sqlite3.connect("combined.db") as conn:
	cursor = conn.cursor()
	cursor.execute("""select ID, TIME_STAMP, RSSI from COMBINED""")
	rows = cursor.fetchall()
	liste = [["ID", "TIME", "RSSI"]]
	for row in rows:
		liste.append([row[0], row[1], row[2]])
liste = zip(*liste)
length = len(liste[0])

with open('test1.csv', 'wb') as testfile:
    csv_writer = csv.writer(testfile)
    for y in range(length):
        csv_writer.writerow([x[y] for x in liste])
	
	


