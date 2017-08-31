The BLUEHYDRA_INSTALL.txt file contains the commands I have used under Raspbian OS to install BlueHydra and other relevant pieces of information like MQTT commands.

The Analysis folder contains databases and the scripts used for their analysis.

The Sensor folder contains the necessary files and folders for the Raspberry Pis.

The Server folder contains the necessary files and folders for the Raspberry Pis.


In all these scripts outdated data include :
- location names: russia, fenetre_casque,...
- IP addresses
- Bluetooth addresses
- database names

Instructions :

A) For real time localization:
You should have :
A folder on your server with every file in the Github folder Bluetoothlocation/Server/Real_time_localization
A folder named Blocation on each RP containing every file of on Bluetoothlocation/Sensor/RPi/Blocation/
(where i is the number you chose for each RP)

0) On each of the RP, do:
cd Blocation
hydra.sh
rpi.sh
(where i is the number in the filename of the sh and python script)
1) On the server, launch traininglive.py and wait until an update of the database automatically generated has taken place.
2) On the server, launch live1.py
3) Enjoy

B) For constituting a database for later analysis:
You should have :
A folder on your server with every file in the Github folder Bluetoothlocation/Server/Traffic_capture/
A folder named Blocation on each RP containing every file of on Bluetoothlocation/Sensor/RPi/Blocation/
(where i is the number you chose for each RP)

0) On each of the RP, do:
cd Blocation
hydra.sh
rpi.sh
(where i is the number in the filename of the sh and python script)
1) On the server, launch training.py 
2) Enjoy
