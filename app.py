import sys
import pymysql

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

def open_worker_tunnel(master_ip, worker_ip):
    tunnel = SSHTunnelForwarder(
        (worker_ip, SSH_PORT),
        ssh_username = "ubuntu",
        ssh_pkey="key.pem",
        remote_bind_address = (master_ip, MYSQL_PORT)
    )
    tunnel.start()
    return tunnel

def direct_hit(query):
    print("Direct hit")

    server = SSHTunnelForwarder(
        HOSTNAMES["master"],
        ssh_username="ubuntu",
        ssh_pkey="key.pem",
        local_bind_address=('127.0.0.1', MYSQL_PORT),
        remote_bind_address=('127.0.0.1', MYSQL_PORT)
    )

    server.start()

    query_mysql('127.0.0.1', MYSQL_PORT, query)

    server.close()

def random():
    print("Random")
    #if ssh_tunnel != None:
    #    ssh_tunnel.stop()

def custom():
    print("Custom")

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
            random(query)
        elif strategy.lower() == "custom":
            custom(query)
        else:
            print("[Error] Invalid strategy. Possible values are: direct, random or custom")
            exit(-1)
    else:
        print("This is a write query. Direct Hit strategy will be used.")
        direct_hit(query)
