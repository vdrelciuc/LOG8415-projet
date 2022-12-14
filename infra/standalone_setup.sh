#!/bin/bash

# Install MySQL Server and sysbench
apt update
apt install mysql-server sysbench -y
systemctl start mysql.service

# Skipped the step where we secure the MySQL instance for simplicity purposes
# MySQL should always be secured in production using: sudo mysql_secure_installation

# Download sakila and load it in MySQL
wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"

# Run sysbench
sysbench oltp_read_write --table-size=1000000 --mysql-db=sakila --db-driver=mysql --mysql-user=root prepare
sysbench oltp_read_write --table-size=1000000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --num-threads=6 --max-time=60 --max-requests=0 run > /home/ubuntu/results.txt
sysbench oltp_read_write --table-size=1000000 --mysql-db=sakila --db-driver=mysql --mysql-user=root cleanup