# This README now includes instructions for setting up cron jobs that stop instances on Friday night at 11:59 PM and start them on Monday morning at 8 AM.


## Steps:
Save the Script: Ensure your manage_instances.py script is saved in a directory, e.g., /home/vmadmin/manage_instances.py.

Prepare the YAML Configuration: Ensure your instances.yaml configuration file is saved in a directory, e.g., /home/vmadmin/instances.yaml.

### Create a Virtual Environment:

```
python3 -m venv /home/vmadmin/myenv
source /home/vmadmin/myenv/bin/activate
pip install boto3 pyyaml
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

