sudo apt-get update
sudo apt install -y unzip

##Reference https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

sudo apt install python3-pip -y
sudo apt install python3.12-venv -y


# Create a virtual environment (if not already created)
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# Install pyyaml
pip install pyyaml

# Install boto3
pip install boto3

# Run the Python script
python manage_instances.py start instances.yaml

# Deactivate the virtual environment when done
deactivate

