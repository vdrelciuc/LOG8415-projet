# LOG8415E -  Advanced Concepts of Cloud Computing

## Getting Started

### Prerequisites

Before using this project, make sure to follow the following steps:

1. Install [Python 3](https://www.python.org/downloads/)
2. Install project dependencies using `pip install boto3`
3. Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
4. Configure your AWS Access Key using `aws configure`
5. Replace `SUBNET_ID` in `cluster_benchmark.py` and `proxy_deploy.py` with your own AWS Subnet (select one with CIDR 172.31.0.0/20)

## Usage

### Standalone MySQL Server Benchmark

To benchmark your standalone MySQL Server instance, simply run `python standalone_benchmark.py`

Once the script is done executing, you can SSH into your Standalone instance. You will find the benchmark output saved under `/home/ubuntu/results.txt`

### MySQL Cluster Benchmark

To benchmark your MySQL Cluster, simply run `python cluster_benchmark.py`

Once the script is done executing, you can SSH into your Manager Node instance. You will find the benchmark output saved under `/home/ubuntu/results.txt`

### Implementing the Proxy Cloud Pattern

To implement the Proxy Cloud Pattern, you will require the same infrastructure as for the MySQL Cluster Benchmark (1 manager node + 3 data nodes) + a Proxy instance. 

If you haven't already done so, start by creating the MySQL Cluster by running `python cluster_benchmark.py`

To create the Proxy instance, simply run `python proxy_deploy.py`

Once the entire infrastructure has been deployed, copy the SSH private key that you used to create the cluster EC2 instances (by default: vockey.pem) from your local machine to the Proxy: `scp -i /local/path/to/vockey.pem ubuntu@<PROXY_PUBLIC_IP>:/home/ubuntu/LOG8415-projet/key.pem`

Then, SSH into the Proxy instance.

From there, you can run the following proxy strategies:
- Direct Hit: `python3 /home/ubuntu/LOG8415-projet/app.py direct [sql_query_between_double_quotes]`
- Random: `python3 /home/ubuntu/LOG8415-projet/app.py random [sql_query_between_double_quotes]`
- Custom: `python3 /home/ubuntu/LOG8415-projet/app.py custom [sql_query_between_double_quotes]`

Note: 
- The Direct Hit strategy will always target the master node. 
- The Random strategy will always target a random worker node.
- The Custom strategy will target the node with the lowest average ping (can be either the master or one of the workers).
- The Proxy will scan the SQL query for a "SELECT" statement, indicator of a read-only request. If no "SELECT" statement is found, the app will automatically shift to a Direct Hit strategy, as write requests (INSERT, DELETE, ALTER, etc.) can only be processed by the master node.
