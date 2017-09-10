# -*- coding: utf-8 -*-

import json
import re
from tabulate import tabulate
from pprint import pprint

interface = ['interface', 'description', 'mode', 'vlans']
interface_list = []

# regex_dis = re.compile(r'^set interfaces +(?P<interface>\S+) +description +(?P<description>\S+)')
regex_des = re.compile(r'^set interfaces +(?P<interface>\S+).*description +(?P<description>\S+)')
regex_mode = re.compile(r'^set interfaces +(?P<interface>\S+).+ethernet-switching +interface-mode +(?P<mode>\S+)')
regex_vlans = re.compile(r'^set interfaces +(?P<interface>\S+).+ethernet-switching +vlan +members +(?P<vlan>[\d+-].+)')
last_interface = ''
interface_desc = None

with open('qfx.txt', mode='r') as f:
    for line in f:
        if 'description' in line:
            match = regex_des.search(line)
            if match:
                if match.group('interface') != last_interface:
                    if last_interface and interface_desc:
                        interface_list.append(interface_desc)
                    last_interface = match.group('interface')
                    interface_desc = {'interface': match.group('interface'),
                                      'description': match.group('description'),
                                      'vlans': []}
        elif 'ethernet-switching interface-mode' in line:
            match = regex_mode.search(line)
            if match:
                if match.group('interface') == last_interface:
                    interface_desc['mode'] = match.group('mode')
        elif 'ethernet-switching vlan members' in line:
            match = regex_vlans.search(line)
            if match:
                if match.group('interface') == last_interface:
                    interface_desc['vlans'].append(match.group('vlan'))
print(tabulate(interface_list, headers='keys', tablefmt='grid'))
# pprint(interface_list)

with open('juniper_qfx.json', 'w') as f:
    json.dump(interface_list, f, sort_keys=True, indent=4)
