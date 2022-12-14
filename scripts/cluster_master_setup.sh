#!/bin/bash

# Installing dependencies
apt update
apt install libaio1 libmecab2 sysbench libncurses5 libtinfo5 -y

# Installing MySQL Cluster Management Server
cd /home/ubuntu
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
rm mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Adding a config for Manager Node
mkdir /var/lib/mysql-cluster
echo "
[ndbd default]
NoOfReplicas=3

[ndb_mgmd]
# Management process options:
hostname=ip-172-31-2-1.ec2.internal # Hostname of manager
datadir=/var/lib/mysql-cluster
NodeId=1

[ndbd]
hostname=ip-172-31-2-2.ec2.internal # Hostname of slave1
NodeId=2
datadir=/usr/local/mysql/data

[ndbd]
hostname=ip-172-31-2-3.ec2.internal # Hostname of slave2
NodeId=3
datadir=/usr/local/mysql/data

[ndbd]
hostname=ip-172-31-2-4.ec2.internal # Hostname of slave3
NodeId=4
datadir=/usr/local/mysql/data


[mysqld]
hostname=ip-172-31-2-1.ec2.internal # MySQL server/client
NodeId=11
" | tee -a /var/lib/mysql-cluster/config.ini

# Creating a service for NDB Management
echo "
[Unit]
Description=MySQL NDB Cluster Management Server
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndb_mgmd -f /var/lib/mysql-cluster/config.ini
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
" | tee -a /etc/systemd/system/ndb_mgmd.service

# Enabling NBD Management service on start
systemctl daemon-reload
systemctl enable ndb_mgmd
systemctl start ndb_mgmd

# Installing MySQL Server Node
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/
cd install

dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

# Pre-allocate root password (blank) so that we can install MySQL Cluster Community Server non-interactively
debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/root-pass password'
debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/re-root-pass password'

dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb

# Configure MySQL Server
echo "
[mysqld]
ndbcluster
bind-address=0.0.0.0
ndb-connectstring=ip-172-31-2-1.ec2.internal  # location of management server

[mysql_cluster]
ndb-connectstring=ip-172-31-2-1.ec2.internal  # location of management server
" | tee -a /etc/mysql/my.cnf

# Enabling MySQL service on start
systemctl restart mysql
systemctl enable mysql

# Download sakila and load it in MySQL
cd /home/ubuntu
wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O /home/ubuntu/sakila-db.tar.gz
tar -xvf /home/ubuntu/sakila-db.tar.gz -C /home/ubuntu/
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;"
mysql -u root -e "SOURCE /home/ubuntu/sakila-db/sakila-data.sql;"

# Run sysbench
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql_storage_engine=ndbcluster prepare
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql_storage_engine=ndbcluster --num-threads=6 --max-time=60 --max-requests=0 run > /home/ubuntu/results.txt
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql_storage_engine=ndbcluster cleanup