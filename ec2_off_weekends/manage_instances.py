import boto3
import yaml
import sys

def get_instance_ids(ec2_client, config):
    instances = set()

    # Fetch instances by IDs directly
    instances.update(config.get('instance_ids', []))

    # Fetch instances by names
    for name in config.get('instance_names', []):
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'tag:Name', 'Values': [name]}]
        )
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.add(instance['InstanceId'])
                print(f"Found instance {instance['InstanceId']} with name {name}")

    # Fetch instances by tags
    for tag in config.get('tags', []):
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': f'tag:{tag}', 'Values': ['*']}
            ]
        )
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.add(instance['InstanceId'])
                print(f"Found instance {instance['InstanceId']} with tag {tag}")

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

    if action == 'start':
        response = ec2_client.start_instances(InstanceIds=instance_ids)
    elif action == 'stop':
        response = ec2_client.stop_instances(InstanceIds=instance_ids)
    else:
        print(f"Error: Invalid action '{action}'. Supported actions: 'start', 'stop'.")
        return

    for instance_id in instance_ids:
        print(f"{action.capitalize()}ing instance {instance_id}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python manage_instances.py <start|stop> <config_file>")
        sys.exit(1)

    action = sys.argv[1]
    config_file = sys.argv[2]

    start_stop_instances(action, config_file)
