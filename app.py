import random
import pymysql
import sys

from pythonping import ping
from sshtunnel import SSHTunnelForwarder

SSH_PORT = 22
MYSQL_PORT = 3306
HOSTNAMES = {
    'master'    : 'ip-172-31-2-1.ec2.internal',
    'worker1'   : 'ip-172-31-2-2.ec2.internal',
    'worker2'   : 'ip-172-31-2-3.ec2.internal',
    'worker3'   : 'ip-172-31-2-4.ec2.internal'
}

def query_mysql(host, port, query):
    connection = pymysql.connect(
        host = host,
        user="root",
        password="MyTemporaryRootPassword",
        db="sakila",
        port=port,
        autocommit=True
    )
    cursor = connection.cursor()
    cursor.execute(query)
    output = cursor.fetchall()
    print(output)
    connection.close()

def open_tunnel_to_master():
    tunnel = SSHTunnelForwarder(
        HOSTNAMES["master"],
        ssh_username="ubuntu",
        ssh_pkey="key.pem",
        local_bind_address=('127.0.0.1', MYSQL_PORT),
        remote_bind_address=('127.0.0.1', MYSQL_PORT)
    )
    tunnel.start()
    return tunnel

def direct_hit(query):
    print("Direct hit strategy was selected.")
    print("We are now connecting to the master node.")

    tunnel = open_tunnel_to_master()
    query_mysql('127.0.0.1', MYSQL_PORT, query)
    tunnel.close()

def random_hit(query):
    print("Random hit strategy was selected.")
    rand = random.randint(1, 3)
    rand_worker = "worker" + str(rand)
    print("We are now randomly connecting to data node {}.".format(rand_worker))
    tunnel = open_tunnel_to_master()
    query_mysql(HOSTNAMES[rand_worker], tunnel.local_bind_port, query)
    tunnel.close()

def get_lowest_ping_instance():
    best_instance = HOSTNAMES["master"]
    lowest_latency_in_ms = 1000
    for key in HOSTNAMES:
        ping_result = ping(HOSTNAMES[key], count=1, timeout=2)
        if ping_result.packet_loss != 1 and ping_result.rtt_avg_ms < lowest_latency_in_ms:
            best_instance = HOSTNAMES[key]
            lowest_latency_in_ms = ping_result.rtt_avg_ms
    return best_instance

def custom_hit(query):
    print("Custom hit strategy was selected.")
    best_instance_hostname = get_lowest_ping_instance()
    best_instance_name = list(HOSTNAMES.keys())[list(HOSTNAMES.values()).index(best_instance_hostname)]
    print("We are now connecting to the data node with the lowest ping: {}".format(best_instance_name))
    tunnel = open_tunnel_to_master()
    query_mysql(HOSTNAMES[best_instance_name], tunnel.local_bind_port, query)
    tunnel.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[Error] You did not specify enough arguments.")
        print("Correct usage is: python3 app.py [strategy] [sql_query_in_double_quotes]")
        print("Possible values for [strategy]: direct, random or custom")
        exit(-1)

    strategy = sys.argv[1]
    query = sys.argv[2]

    if "select" in query.lower():
        print("This is a read-only query. Any strategy can be used.")
        if strategy.lower() == "direct":
            direct_hit(query)
        elif strategy.lower() == "random":
            random_hit(query)
        elif strategy.lower() == "custom":
            custom_hit(query)
        else:
            print("[Error] Invalid strategy. Possible values are: direct, random or custom")
            exit(-1)
    else:
        print("This is a write query. Direct Hit strategy will be used.")
        direct_hit(query)
