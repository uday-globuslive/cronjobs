- This README now includes instructions for setting up cron jobs that stop instances on Friday night at 11:59 PM and start them on Monday morning at 8 AM.
- Along with above step, it does kuerbernetes nodes draining before stopping the instances.
- Previous script works if kubectl configured on the same machine where the cron job runs.
- If kuebrnetes cluster is in one vpc and my ec2 instance from where this python file is running is in another vpc. Now, kubectl commands won't run directly.
- To run kubectl commands from your Python script when the Kubernetes cluster and the script are in different VPCs, you can use a few approaches. Here is a step-by-step guide on how to set this up:

### Approach we follow: SSH into the Jumpbox and Run Commands
- Set Up VPC Peering: Ensure the VPCs are peered and the appropriate routes and security groups are configured to allow traffic between them.
- SSH from Python to Jumpbox: Use a library like paramiko to SSH into the jumpbox from your Python script and run kubectl commands.
- Here is an example Python script using paramiko:
```
import paramiko

# Define your jumpbox details
jumpbox_ip = 'jumpbox_public_ip'
jumpbox_user = 'ec2-user'
jumpbox_key_path = '/path/to/your/private/key.pem'

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(jumpbox_ip, username=jumpbox_user, key_filename=jumpbox_key_path)

# Define the kubectl command you want to run
kubectl_command = 'kubectl get pods -n your-namespace'

# Run the command on the jumpbox
stdin, stdout, stderr = ssh.exec_command(kubectl_command)

# Print the command output
print(stdout.read().decode())
print(stderr.read().decode())

# Close the SSH connection
ssh.close()
```


## Steps:
Save the Script: Ensure your manage_instances.py script is saved in a directory, e.g., /home/vmadmin/manage_instances.py.

Prepare the YAML Configuration: Ensure your instances.yaml configuration file is saved in a directory, e.g., /home/vmadmin/instances.yaml.

### Create a Virtual Environment:

```
python3 -m venv /home/vmadmin/myenv
source /home/vmadmin/myenv/bin/activate
pip install boto3 pyyaml paramiko
```
### Make the Script Executable:
```
chmod +x /home/vmadmin/manage_instances.py
```

### Test the Script: Run the script manually to ensure it works:
```
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py start /home/vmadmin/instances.yaml
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py stop /home/vmadmin/instances.yaml
```

Create Shell Scripts for Cron Jobs:

- Start Instances (start_instances.sh):
```
#!/bin/bash
source /home/vmadmin/myenv/bin/activate
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py start /home/vmadmin/instances.yaml >> /home/vmadmin/start_instances.log 2>&1
```

- Stop Instances (stop_instances.sh):
```
#!/bin/bash
source /home/vmadmin/myenv/bin/activate
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py stop /home/vmadmin/instances.yaml >> /home/vmadmin/stop_instances.log 2>&1
```

- Make both scripts executable:
```
chmod +x /home/vmadmin/start_instances.sh
chmod +x /home/vmadmin/stop_instances.sh
```

- Check the log files after the cron job is scheduled to run to see if there is any output indicating success or failure.
```
cat /home/vmadmin/start_instances.log
cat /home/vmadmin/stop_instances.log
```

- Create Cron Jobs: Open the cron job configuration for the vmadmin user:
```
crontab -e
```

### Add the following lines to the crontab file to set up the jobs:

- Start Instances on Monday at 8 AM:
```
0 8 * * 1 /home/vmadmin/start_instances.sh
```
- Stop Instances on Friday at 11:59 PM:
```
59 23 * * 5 /home/vmadmin/stop_instances.sh
```

- To manually start or stop instances, run:
```
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py start /home/vmadmin/instances.yaml
/home/vmadmin/myenv/bin/python /home/vmadmin/manage_instances.py stop /home/vmadmin/instances.yaml
```



# Kubernetes Node Draining

When working with Kubernetes clusters, it's crucial to drain nodes before stopping their instances. Failing to do so can lead to a range of issues, from application disruptions to cluster instability. This document outlines the potential problems and provides steps to properly drain a node.

## Potential Issues When Not Draining a Node

### Disrupted Applications
- **Abrupt Termination**: Pods running on the node will be abruptly terminated, leading to application or service downtime.
- **Data Loss**: Stateful applications might experience data loss or corruption due to improper termination.

### Pod Rescheduling Delays
- **Detection Time**: Kubernetes takes time to detect that a node is down (node eviction timeout) and reschedule the pods, causing application unavailability during this period.
- **Service Restoration Delay**: The delay in rescheduling can significantly affect service availability.

### Unclean Shutdown
- **Incomplete Shutdown Procedures**: Pods do not get a chance to handle termination signals properly, potentially leading to issues like unclosed database connections or unreleased resources.

### Disrupted Services
- **Critical System Pods**: If the node was hosting critical system pods (DNS, logging, monitoring), their abrupt termination could impact the overall cluster functionality.

### Cluster Instability
- **Multiple Node Failures**: Stopping multiple nodes without draining can cause cluster-wide issues, making the entire Kubernetes cluster unstable or even causing a partial or full outage.

## Example Scenarios
- **Web Applications**: Users might experience interrupted sessions if a web server pod is abruptly terminated.
- **Database Pods**: Terminating a database pod in the middle of a transaction can cause incomplete transactions and potential data inconsistencies.
- **Stateful Services**: Stateful services like Cassandra or Kafka might suffer from data loss or require lengthy recovery procedures to become consistent again.

## Node Draining
Node draining is the recommended practice to handle these issues effectively. 

### Benefits of Node Draining
- **Graceful Termination**: Kubernetes sends termination signals to the pods, allowing them to gracefully shut down, close connections, and release resources.
- **Pod Rescheduling**: Kubernetes proactively reschedules the pods on other available nodes before the node is stopped, ensuring continuous availability of services.
- **Minimized Disruption**: Services experience minimal disruption, and the cluster remains stable and functional.

### Steps to Drain a Node
1. **Drain Command**:
   Use the following command to gracefully evict pods from the node:
   ```sh
   kubectl drain <node-name> --ignore-daemonsets --delete-local-data --force
   ```
 - --ignore-daemonsets: Ignores DaemonSet-managed pods.
 - --delete-local-data: Deletes local data.
 - --force: Handles pods that might not have Pod Disruption Budgets (PDBs) configured.
2. **Monitor Pod Eviction**: Monitor the eviction process to ensure all pods are rescheduled properly.
3. **Stop Instance**: Once the node is drained and all pods are rescheduled, stop the EC2 instance.
