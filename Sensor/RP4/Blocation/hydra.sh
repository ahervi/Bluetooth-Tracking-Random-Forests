#!/bin/bash

cd blue_hydra
sudo rm blue_hydra_rssi.log
while true; do sudo ./bin/blue_hydra; done