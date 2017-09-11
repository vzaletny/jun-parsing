# -*- coding: utf-8 -*-

import argparse
import json
import re
from tabulate import tabulate
import unicodecsv as csv


def convert(filename):
    """
    Convert QFX configuration file to some readable formats for the following analysis
    :param filename: Juniper QFX configuration file
    :return: Create JSON, TXT, CSV and HTML translated files
    """
    interface_list = []
    regex_des = re.compile(r'^set interfaces +(?P<interface>\S+).*description +(?P<description>\S+)')
    regex_mode = re.compile(r'^set interfaces +(?P<interface>\S+).+ethernet-switching +interface-mode +(?P<mode>\S+)')
    regex_vlans = re.compile(
        r'^set interfaces +(?P<interface>\S+).+ethernet-switching +vlan +members +(?P<vlan>[\d+-].+)')
    regex_irb = re.compile(
        r'^set interfaces +(?P<interface>\S+) +unit (?P<unit>\d+).*description +(?P<description>\S+)')
    regex_irb_ip = re.compile(r'^set interfaces +(?P<interface>\S+) +unit (?P<unit>\d+).*address +(?P<ip>[\d.]+/\d+)')

    last_interface = ''
    interface_desc = None
    last_unit = '0'
    ip = ''

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:
            if 'description' in line:
                match = regex_des.search(line)
                if 'irb' in line:
                    match = regex_irb.search(line)
                    last_unit = match.group('unit')
                if match:
                    if match.group('interface') != last_interface or last_unit != '0':
                        if last_interface and interface_desc:
                            interface_list.append(interface_desc)
                        last_interface = match.group('interface')
                        interface_desc = {'interface': match.group('interface'),
                                          'description': match.group('description'),
                                          'vlans': '',
                                          'unit': last_unit,
                                          'ip': ip,
                                          'тест': 'тестовое поле'}
            elif 'ethernet-switching interface-mode' in line:
                match = regex_mode.search(line)
                if match:
                    if match.group('interface') == last_interface:
                        interface_desc['mode'] = match.group('mode')
            elif 'ethernet-switching vlan members' in line:
                match = regex_vlans.search(line)
                if match:
                    if match.group('interface') == last_interface:
                        # interface_desc['vlans'].append(match.group('vlan'))
                        if not interface_desc['vlans']:
                            interface_desc['vlans'] = match.group('vlan')
                        else:
                            interface_desc['vlans'] += (',' + match.group('vlan'))
            elif 'family inet address' in line:
                match = regex_irb_ip.search(line)
                if match:
                    if match.group('unit') == last_unit and match.group('interface') == last_interface:
                        interface_desc['ip'] = match.group('ip')
                        # print(match.group('interface'), match.group('unit'), match.group('ip'))

    grid_txt = tabulate(interface_list, headers='keys', tablefmt='grid')
    with open('juniper_qfx.txt', 'w', encoding='utf-8') as f:
        f.write(grid_txt)

    html_out = tabulate(interface_list, headers='keys', tablefmt='html')
    with open('juniper_gfx.html', 'w', encoding='utf-8') as f:
        f.write(html_out)

    with open('juniper_qfx.json', 'w', encoding='utf-8') as f:
        json.dump(interface_list, f, sort_keys=True, indent=4, ensure_ascii=False)

    with open('juniper_qfx.csv', 'wb') as f:
        writer = csv.DictWriter(f, quoting=csv.QUOTE_NONNUMERIC, fieldnames=interface_list[0], delimiter=';')
        writer.writeheader()
        writer.writerows(interface_list)


def getargs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description='Process args for getting input Juniper QFX file to convert in different formats')
    parser.add_argument('-f', '--filename', required=True, action='store',
                        help='Input Juniper QFX file to convert')
    args = parser.parse_args()
    return args


def main():
    """
    Simple command-line program for converting Juniper QFX file.
    """
    convert(getargs().filename)
    return 0


# Start program
if __name__ == "__main__":
    main()
