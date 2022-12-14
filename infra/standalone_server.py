import boto3
import time

ec2_client = boto3.client("ec2", region_name="us-east-1")

def read_user_data():
    with open("standalone_setup.sh", "r") as file:
        user_data = file.read()
    return user_data

def create_or_retreive_security_group():
    existing_security_group = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['standalone-security-group'])
        ]
    )

    if len(existing_security_group['SecurityGroups']) > 0:
        security_group = existing_security_group['SecurityGroups'][0]
    else:
        security_group = ec2_client.create_security_group(
            GroupName='standalone-security-group',
            Description='standalone-security-group'
        )

        # open inbound SSH port
        ec2_client.authorize_security_group_ingress(
            CidrIp="0.0.0.0/0",
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22,
            GroupName='standalone-security-group'
        )

    return security_group

def launch_instance(security_group_id):
    instance = ec2_client.run_instances(
        ImageId="ami-0ee23bfc74a881de5", # Ubuntu 18.04 LTS
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="vockey",
        UserData=read_user_data(),
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'standalone'
                },
            ]
        },
        ]
    )

    return instance

if __name__ == "__main__":
    # create security group
    security_group = create_or_retreive_security_group()

    # launch EC2 instance
    instance = launch_instance(security_group['GroupId'])

    # display instance info
    print("Running...")
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance["Instances"][0]["InstanceId"]])
    print("Standalone server successfully launched")
    print(instance["Instances"][0]["InstanceId"])