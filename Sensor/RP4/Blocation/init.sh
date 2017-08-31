#!/bin/bash
sudo rm -rf blue_hydra
git clone https://github.com/pwnieexpress/blue_hydra.git
cd blue_hydra
bundle install
sudo ./bin/blue-hydra

