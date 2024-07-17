import boto3
import yaml
import sys
import subprocess
from botocore.exceptions import ClientError

def kubectl_drain(node_name):
    try:
        subprocess.run(["kubectl", "drain", node_name, "--ignore-daemonsets", "--delete-local-data", "--force"], check=True)
        print(f"Drained node {node_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error draining node {node_name}: {e}")

def kubectl_uncordon(node_name):
    try:
        subprocess.run(["kubectl", "uncordon", node_name], check=True)
        print(f"Uncordoned node {node_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error uncordoning node {node_name}: {e}")

def get_private_ip(ec2_client, instance_id):
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        return response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    except ClientError as e:
        print(f"Error getting private IP for instance {instance_id}: {e}")
        return None

def get_node_name_from_ip(private_ip):
    formatted_ip = private_ip.replace('.', '-')
    try:
        result = subprocess.run(
            ["kubectl", "get", "nodes", "-o", "jsonpath={.items[?(@.metadata.name==\"ip-" + formatted_ip + "\")].metadata.name}"],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting node name for IP {private_ip}: {e}")
        return None

def get_instance_ids(ec2_client, config):
    instances = set()
    found_names = set()
    found_tags = set()

    # Fetch instances by IDs directly
    instances.update(config.get('instance_ids', []))

    # Fetch instances by names
    for name in config.get('instance_names', []):
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'tag:Name', 'Values': [name]}]
        )
        if response['Reservations']:
            found_names.add(name)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.add(instance['InstanceId'])
                print(f"Found instance {instance['InstanceId']} with name {name}")

    for name in config.get('instance_names', []):
        if name not in found_names:
            print(f"No instances found with name {name}")

    # Fetch instances by tags
    for tag in config.get('tags', []):
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': f'tag:{tag}', 'Values': ['*']},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        )
        if response['Reservations']:
            found_tags.add(tag)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.add(instance['InstanceId'])
                print(f"Found instance {instance['InstanceId']} with tag {tag}")

    for tag in config.get('tags', []):
        if tag not in found_tags:
            print(f"No instances found with tag {tag}")

    return list(instances)

def start_stop_instances(action, config_file):
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        return

    region = config.get('region', None)
    profile = config.get('profile', None)

    session = boto3.Session(region_name=region, profile_name=profile)
    ec2_client = session.client('ec2')

    instance_ids = get_instance_ids(ec2_client, config)

    for instance_id in instance_ids:
        try:
            private_ip = get_private_ip(ec2_client, instance_id)
            node_name = get_node_name_from_ip(private_ip) if private_ip else None

            if action == 'start':
                response = ec2_client.start_instances(InstanceIds=[instance_id])
                print(f"Starting instance {instance_id}")
                if node_name:
                    kubectl_uncordon(node_name)
            elif action == 'stop':
                if node_name:
                    kubectl_drain(node_name)
                response = ec2_client.stop_instances(InstanceIds=[instance_id])
                print(f"Stopping instance {instance_id}")
            else:
                print(f"Error: Invalid action '{action}'. Supported actions: 'start', 'stop'.")
                return
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                print(f"Instance {instance_id} not found. Skipping.")
            elif e.response['Error']['Code'] == 'InvalidInstanceID.Malformed':
                print(f"Instance ID {instance_id} is malformed. Skipping.")
            else:
                print(f"Error {action}ing instance {instance_id}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python manage_instances.py <start|stop> <config_file>")
        sys.exit(1)

    action = sys.argv[1]
    config_file = sys.argv[2]

    start_stop_instances(action, config_file)
