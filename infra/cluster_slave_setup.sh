#!/bin/bash

# Installing dependencies
apt update
apt install libclass-methodmaker-perl libaio1 libmecab2  -y

# Installing MySQL Cluster Data Node
cd /home/ubuntu
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb
dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb
rm mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

# Adding a config for Data Node
( echo "[mysql_cluster]"; echo "ndb-connectstring=ip-172-31-2-1.ec2.internal" ) | tee -a /etc/my.cnf

# Creating Data Node folder
mkdir -p /usr/local/mysql/data

# Creating a service for NDBD
( echo "[Unit]"; 
echo "Description=MySQL NDB Data Node Daemon";
echo "After=network.target auditd.service";
echo "";
echo "[Service]";
echo "Type=forking";
echo "ExecStart=/usr/sbin/ndbd";
echo "ExecReload=/bin/kill -HUP $MAINPID";
echo "KillMode=process";
echo "Restart=on-failure";
echo "";
echo "[Install]";
echo "WantedBy=multi-user.target" ) | tee -a /etc/systemd/system/ndbd.service

# Enabling NDBD service on start
systemctl daemon-reload
systemctl enable ndbd
systemctl start ndbd