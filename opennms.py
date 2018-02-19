#!/usr/bin/env python

'''
OpenNMS dynamic inventory
Query OpenNMS REST API to obtain nodes and categories

'''

import os
import sys
import argparse
import requests
import time

try:
    import json
except ImportError:
    import simplejson as json

class OPENNMSInventory(object):

    def __init__(self):
        self.transport = "http://"
        self.opennms_ip = "server_ip"
        self.opennms_port = "8980"
        self.username = "user"
        self.password = "password"
        self.headers = {"Accept": "application/json"}
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.get_discovered_devices()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print json.dumps(self.inventory);

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    def genericGET(self, URL):
        """
         Issue an HTTP GET base on the URL passed as an argument and example in cURL is:

         $ curl -k https://<opennms_ip>/opennms/rest/nodes
        """
        URL = "%s%s:%s%s" % (self.transport, self.opennms_ip, self.opennms_port, URL)
        try:
            r = requests.get(URL, headers=self.headers, auth=(self.username, self.password))
        except requests.ConnectionError as e:
            return (False, e)
        return (r.status_code, r.json())


    def get_discovered_devices(self):
        """ Query OpenNMS server for all nodes.

            For information on the response body, see the API documentation on:
            http://wiki.opennms.org/wiki/ReST

        """
        # dictionary for the complete result
        result = { }

        # dictionary for hostvars
        hostvars = { }

        # list for all available categories on OpenNMS
        groups_list = [ ]

        # dictionary to insert in result
        groups = { }

        # query OpenNMS for nodes
        status, response = self.genericGET("/opennms/rest/nodes?limit=0")
        for node in response['node']:
            try:
                hostvars[node['label']] = { }
                facts = {'description': node["sysDescription"],
                         'location': node["sysLocation"],
                         'device_ip': "0.0.0.0"
                        }
                # query OpenNMS for ipinterfaces
                URL = "/opennms/rest/nodes/%s/ipinterfaces?limit=0" % (node["id"])
                status, ipinterfaces = self.genericGET(URL)
                for ipinterface in ipinterfaces['ipInterface']:
                    if ipinterface["snmpPrimary"] == "P":
                        facts.update({'device_ip': ipinterface["ipAddress"]})
                hostvars[node["label"]].update(facts)
                # add node to categories if set
                for category in node['categories']:
                    if not category["name"] in groups_list:
                        groups_list.append(category["name"])
                        groups.update({ category["name"]: { 'hosts': [ ], 'vars': { } }})
                    groups[category["name"]]["hosts"].append(node["label"])


            except KeyError:
                pass


        # at first set the groups (in our case categories) to the result
        result = groups

        # now insert the meta-data (host variables) for each host
        result.update({ '_meta': { 'hostvars': hostvars }})

        return result

if __name__ == '__main__':
    # Get the inventory.
    OPENNMSInventory()
