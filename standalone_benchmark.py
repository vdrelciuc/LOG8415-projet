import boto3

ec2_client = boto3.client("ec2", region_name="us-east-1")

def read_user_data():
    # Read user data script for the Standalone MySQL Server
    with open("scripts/standalone_setup.sh", "r") as file:
        user_data = file.read()
    return user_data

def create_or_retreive_security_group():
    # Function to retreive an existing security group or to create it if it doesn't exist
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
    # Launch an EC2 instance
    instance = ec2_client.run_instances(
        ImageId="ami-0ee23bfc74a881de5",
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

def display_info(instance):
    # Display script completion information after the instances are done being created
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance["Instances"][0]["InstanceId"]])
    print("Done.")
    print("Standalone benchmark results are available under: /home/ubuntu/results.txt")

if __name__ == "__main__":
    # create security group
    security_group = create_or_retreive_security_group()

    # launch EC2 instance
    instance = launch_instance(security_group['GroupId'])

    # display instance info
    print("Running...")
    display_info(instance)