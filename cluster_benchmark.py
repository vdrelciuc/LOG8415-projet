import boto3

ec2_client = boto3.client("ec2", region_name="us-east-1")

SUBNET_ID = 'subnet-0d4dd60cd5b5b4377' # replace with your own AWS subnet (CIDR 172.31.0.0/20)

def read_master_user_data():
    # Read user data script for Cluster Master node
    with open("scripts/cluster_master_setup.sh", "r") as file:
        user_data = file.read()
    return user_data

def read_slave_user_data():
    # Read user data script for Cluster Data node
    with open("scripts/cluster_worker_setup.sh", "r") as file:
        user_data = file.read()
    return user_data

def create_or_retreive_security_group():
    # Function to retreive an existing security group or to create it if it doesn't exist
    existing_security_group = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['cluster-security-group'])
        ]
    )

    if len(existing_security_group['SecurityGroups']) > 0:
        security_group = existing_security_group['SecurityGroups'][0]
    else:
        security_group = ec2_client.create_security_group(
            GroupName='cluster-security-group',
            Description='cluster-security-group'
        )

        # open inbound SSH port
        ec2_client.authorize_security_group_ingress(
            CidrIp="0.0.0.0/0",
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22,
            GroupName='cluster-security-group'
        )

        # open inboud MySQL port
        ec2_client.authorize_security_group_ingress(
            CidrIp="172.31.1.0/20",
            IpProtocol='-1',
            FromPort=3306,
            ToPort=3306,
            GroupName='cluster-security-group'
        )

        # open inboud MySQL Cluster Auto Installer port
        ec2_client.authorize_security_group_ingress(
            CidrIp="172.31.1.0/20",
            IpProtocol='-1',
            FromPort=8081,
            ToPort=8081,
            GroupName='cluster-security-group'
        )

        # open inboud NBD Management Server port
        ec2_client.authorize_security_group_ingress(
            CidrIp="172.31.1.0/20",
            IpProtocol='-1',
            FromPort=1186,
            ToPort=1186,
            GroupName='cluster-security-group'
        )

    return security_group

def launch_instance(name, security_group_id, private_ip, user_data):
    # Launch an EC2 instance
    return ec2_client.run_instances(
        ImageId="ami-0a6b2839d44d781b2",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="vockey",
        UserData=user_data,
        SecurityGroupIds=[security_group_id],
        SubnetId=SUBNET_ID, 
        PrivateIpAddress=private_ip,
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': name
                },
            ]
        },
        ]
    )

def display_info(master, slave1, slave2, slave3):
    # Display script completion information after the instances are done being created
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[master["Instances"][0]["InstanceId"]])
    waiter.wait(InstanceIds=[slave1["Instances"][0]["InstanceId"]])
    waiter.wait(InstanceIds=[slave2["Instances"][0]["InstanceId"]])
    waiter.wait(InstanceIds=[slave3["Instances"][0]["InstanceId"]])
    print("Done.")
    print("Cluster benchmark results are available on master node under: /home/ubuntu/results.txt")

if __name__ == "__main__":
    # create security group
    private_security_group = create_or_retreive_security_group()

    # launch EC2 instances
    security_group_id = private_security_group['GroupId']
    master = launch_instance("master", security_group_id, "172.31.2.1", read_master_user_data())
    slave1 = launch_instance("slave1", security_group_id, "172.31.2.2", read_slave_user_data())
    slave2 = launch_instance("slave2", security_group_id, "172.31.2.3", read_slave_user_data())
    slave3 = launch_instance("slave3", security_group_id, "172.31.2.4", read_slave_user_data())

    # display instances info
    print("Running...")
    display_info(master, slave1, slave2, slave3)