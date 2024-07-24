Here's a Python script that does below steps:

- Automates the entire process of creating backups, draining the Kubernetes node, terminating the instance, restoring data on a new instance, and joining the new node to the Kubernetes cluster. 

- The script uses Boto3 for AWS operations and Paramiko for SSH operations.

- Use a tag to identify the specific EC2 instance that we want to backup and later terminate.

- Find the instance ID dynamically based on this tag.

- Store necessary information to handle the next iteration after a weekend.

Prerequisites:
1. Install required Python packages:
```
pip install boto3 paramiko
```
2. Ensure AWS credentials are configured on the machine where the script will run (e.g., using aws configure).
```
import boto3
import paramiko
import time
from datetime import datetime

# Constants
SOURCE_FOLDER = "/path/to/source/folder"
DESTINATION_INSTANCE = "destination-instance-ip"
DESTINATION_FOLDER = "/path/to/destination/folder"
BACKUP_FILE = f"backup_{datetime.now().strftime('%F')}.tar.gz"

# AWS configuration
REGION = "your-region"
INSTANCE_TYPE = "g5.2xlarge"
KEY_NAME = "your-key-pair"
SECURITY_GROUP_IDS = ["your-security-group-id"]
SUBNET_ID = "your-subnet-id"
AMI_ID = "your-ami-id"
MASTER_IP = "your-master-ip"
MASTER_PORT = "your-master-port"
KUBEADM_TOKEN = "your-kubeadm-token"
CA_CERT_HASH = "your-ca-cert-hash"

# Boto3 clients
ec2 = boto3.client('ec2', region_name=REGION)

def create_backup():
    # SSH into the source instance and create a backup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('source-instance-ip', username='your-username', key_filename='/path/to/key.pem')

    commands = [
        f"tar -czf /tmp/{BACKUP_FILE} -C {SOURCE_FOLDER} .",
        f"scp /tmp/{BACKUP_FILE} {DESTINATION_INSTANCE}:{DESTINATION_FOLDER}",
        f"rm /tmp/{BACKUP_FILE}"
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

    ssh.close()

def drain_node(node_name):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('source-instance-ip', username='your-username', key_filename='/path/to/key.pem')

    command = f"kubectl drain {node_name} --ignore-daemonsets --delete-emptydir-data"
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

def terminate_instance(instance_id, volume_id):
    ec2.terminate_instances(InstanceIds=[instance_id])
    ec2.delete_volume(VolumeId=volume_id)

def create_new_instance_and_volume():
    # Create a new EBS volume
    volume = ec2.create_volume(Size=50, AvailabilityZone=REGION, VolumeType='gp2')
    volume_id = volume['VolumeId']

    # Create a new EC2 instance and attach the new EBS volume
    instance = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=SECURITY_GROUP_IDS,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sdf',
                'Ebs': {
                    'VolumeSize': 50,
                }
            }
        ],
        MinCount=1,
        MaxCount=1
    )
    instance_id = instance['Instances'][0]['InstanceId']

    # Wait for the instance to be running
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    return instance_id, volume_id

def restore_backup(new_instance_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(new_instance_ip, username='your-username', key_filename='/path/to/key.pem')

    commands = [
        f"scp {DESTINATION_INSTANCE}:{DESTINATION_FOLDER}/{BACKUP_FILE} /tmp/",
        f"tar -xzf /tmp/{BACKUP_FILE} -C {SOURCE_FOLDER}",
        f"rm /tmp/{BACKUP_FILE}"
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

    ssh.close()

def join_kubernetes_cluster(new_instance_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(new_instance_ip, username='your-username', key_filename='/path/to/key.pem')

    command = f"sudo kubeadm join {MASTER_IP}:{MASTER_PORT} --token {KUBEADM_TOKEN} --discovery-token-ca-cert-hash sha256:{CA_CERT_HASH}"
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

if __name__ == "__main__":
    create_backup()

    node_name = "your-node-name"
    drain_node(node_name)

    instance_id = "your-instance-id"
    volume_id = "your-volume-id"
    terminate_instance(instance_id, volume_id)

    new_instance_id, new_volume_id = create_new_instance_and_volume()

    # Retrieve new instance public IP
    instance_info = ec2.describe_instances(InstanceIds=[new_instance_id])
    new_instance_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']

    restore_backup(new_instance_ip)
    join_kubernetes_cluster(new_instance_ip)

```
Notes:
- Replace the placeholder values ('your-...') with actual values relevant to your environment.
Ensure that the SSH keys are correctly configured and accessible.
- Modify paths and other configuration settings as per your setup.

This script will automate the entire process, making it easier to manage your Kubernetes node and backup/restore operations.