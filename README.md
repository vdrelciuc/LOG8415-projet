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

Once the entire infrastructure has been deployed, SSH into your Proxy instance. From there, you can run the following proxy strategies:
- Direct Hit: `python /home/ubuntu/proxy_run.py -direct`
- Random: `python /home/ubuntu/proxy_run.py -random`
- Customized: `python /home/ubuntu/proxy_run.py -custom`

If no option is specifyed when calling `proxy_run.py`, it will default to the Direct Hit strategy.

Note: 
- The Direct Hit strategy will launch 2 SQL queries (1 INSERT + 1 SELECT), both targeted at the master node. 
- The Customized strategy will also launch 2 SQL queries (1 INSERT + 1 SELECT). The INSERT will automatically be targeted at the master node, as it's the only node that supports writing data, while the SELECT will be targeted to the instance with the lowest response time (master or worker). 
- The Random strategy will launch a single SQL query (1 SELECT), targeted only at a random worker.
