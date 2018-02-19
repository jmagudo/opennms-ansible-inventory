# opennms-ansible-inventory
OpenNMS Ansible dynamic inventory script

Based in https://github.com/smnmtzgr/ansible-apicem-dynamic-inventory code

Python script you can use OpenNMS as a dynamic inventory for ansible. 
I used code from https://github.com/smnmtzgr/ansible-apicem-dynamic-inventory.

## usage
1. Place the file opennms.py in a folder at your ansible-project.
2. Edit the file and change the variables: self.transport, self.opennms_ip, self.opennms_port, self.username and self.password to your own OpenNMS installation values.
3. Execute a playbook with OpenNMS as the dynamic inventory.

## examples

ansible-playbook -i opennms.py test.yml

## returned variables

In this version the following variables are returned by the dynamic inventory as host variables:

* description
* location
* device_ip

Also all the categories present in OpenNMS are returned.
