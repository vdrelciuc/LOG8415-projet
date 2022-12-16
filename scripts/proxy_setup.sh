#!/bin/bash

# Install dependencies
apt update -y
apt install python3 python3-pip git -y
pip install pymysql sshtunnel pythonping

# Clone Git project containing app.py
cd /home/ubuntu
git clone https://github.com/vdrelciuc/LOG8415-projet.git

# Don't forget to copy the SSH Private Key used for launching 
# the Master Node EC2 instance under /home/ubuntu/LOG8415-projet/key.app 
# before running the proxy