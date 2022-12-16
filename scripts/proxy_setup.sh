#!/bin/bash

apt update -y
apt install python3 python3-pip git -y
pip install pymysql sshtunnel pythonping

cd /home/ubuntu
git clone https://github.com/vdrelciuc/LOG8415-projet.git