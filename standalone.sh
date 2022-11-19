#!/bin/bash

MYSQL_PASSWORD=StrongTemporaryPassword321!

# Install MySQL Server
apt update
apt install mysql-server -y
systemctl start mysql.service

# Secure MySQL Server (same functionality as mysql_secure_installation):
# Set root password
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_PASSWORD';"
# Kill the anonymous users
mysql -u root -p$MYSQL_PASSWORD -e "DELETE FROM mysql.user WHERE User='';"
# Block remote login for root
mysql -u root -p$MYSQL_PASSWORD -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
# Kill off the demo database
mysql -u root -p$MYSQL_PASSWORD -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"

# Setup Sakila demo database
wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/
mysql -u root -p$MYSQL_PASSWORD -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
mysql -u root -p$MYSQL_PASSWORD -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"

# Setup and run Sysbench
apt-get install sysbench -y
sysbench oltp_read_write --table-size=1000000 --mysql-db=sakila --mysql-user=root --mysql-password=$MYSQL_PASSWORD prepare
sysbench oltp_read_write --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root --mysql-password=$MYSQL_PASSWORD run > /home/ubuntu/results.txt

# Make our security changes take effect (running this before running Sysbench breaks it)
mysql -u root -p$MYSQL_PASSWORD -e "FLUSH PRIVILEGES;"