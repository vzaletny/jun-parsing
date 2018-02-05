"""
    Convert QFX configuration file to some readable formats for
    the following analysis
    :param: filename - Juniper QFX configuration file
    :return: Create JSON, TXT, CSV and HTML translated files
"""
import argparse
import json
import re
from tabulate import tabulate
import unicodecsv as csv
import os.path
import pandas as pd


def convert(filename):
    regex_des = re.compile(r'^set interfaces +(?P<interface>\S+)'
                           r'.*description +(?P<description>\S+)'
                           )
    regex_mode = re.compile(r'^set interfaces +(?P<interface>\S+)'
                            r'.+ethernet-switching +interface-mode'
                            r' +(?P<mode>\S+)'
                            )
    regex_vlans = re.compile(r'^set interfaces +(?P<interface>\S+)'
                             r'.+ethernet-switching +vlan +members'
                             r' +(?P<vlan>[\d+-].+)'
                             )
    regex_irb = re.compile(r'^set interfaces +(?P<interface>\S+) '
                           r'+unit (?P<unit>\d+)'
                           r'.*description +(?P<description>\S+)'
                           )
    regex_irb_ip = re.compile(r'^set interfaces +(?P<interface>\S+)'
                              r' +unit (?P<unit>\d+)'
                              r'.*address +(?P<ip>[\d.]+/\d+)'
                              )
    interfaces_list = []
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
                    if match.group('interface') != last_interface \
                            or last_unit != '0':
                        if last_interface and interface_desc:
                            interfaces_list.append(interface_desc)
                        last_interface = match.group('interface')
                        interface_desc = {
                            'interface': match.group('interface'),
                            'description': match.group('description'),
                            'vlans': '',
                            'unit': last_unit,
                            'ip': ip
                            }
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
                            interface_desc['vlans'] += (','
                                                        + match.group('vlan')
                                                        )
            elif 'family inet address' in line:
                match = regex_irb_ip.search(line)
                if match:
                    if match.group('unit') == last_unit \
                            and match.group('interface') == last_interface:
                        interface_desc['ip'] = match.group('ip')
                        # print(match.group('interface'), match.group('unit'),
                        #  match.group('ip'))
    return interfaces_list


def save_to_txt(filename, interface_list):
    grid_txt = tabulate(interface_list, headers='keys', tablefmt='grid')
    with open(f'{filename}.txt', 'w', encoding='utf-8') as file_handler:
        file_handler.write(grid_txt)


def save_to_html(filename, interface_list):
    html_out = tabulate(interface_list, headers='keys', tablefmt='html')
    with open(f'{filename}.html', 'w', encoding='utf-8') as file_handler:
        file_handler.write(html_out)


def save_to_json(filename, interface_list):
    with open(f'{filename}.json', 'w', encoding='utf-8') as file_handler:
        json.dump(interface_list,
                  file_handler,
                  sort_keys=True,
                  indent=4,
                  ensure_ascii=False
                  )


def save_to_csv(filename, interface_list):
    with open(f'{filename}.csv', 'wb') as file_handler:
        writer = csv.DictWriter(file_handler,
                                quoting=csv.QUOTE_NONNUMERIC,
                                fieldnames=interface_list[0],
                                delimiter=';'
                                )
        writer.writeheader()
        writer.writerows(interface_list)


def save_to_xlsx(filename, interface_list):
    df = pd.DataFrame(interface_list)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(path=f'{filename}.xlsx', engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def save_to_files(filename, interface_list):
    save_to_func_list = [
        save_to_txt,
        save_to_html,
        save_to_json,
        save_to_csv,
        save_to_xlsx
    ]
    for save_to in save_to_func_list:
        try:
            save_to(filename, interface_list)
        except OSError as error:
            print('Something went wrong')
            exit(error)


def getargs():
    parser = argparse.ArgumentParser(
        description='Input Juniper QFX file to convert in different formats'
    )
    parser.add_argument('-f',
                        '--file',
                        required=True,
                        action='store',
                        help='Input Juniper QFX file to convert'
                        )
    args = parser.parse_args()
    return args


def _main():
    filename = getargs().file
    try:
        interface_list = convert(filename)
    except FileNotFoundError:
        exit('File not found')
    except OSError as error:
        print('Something went wrong')
        exit(error)
    else:
        filename = f'{os.path.splitext(filename)[0]}_convert_to_'
        save_to_files(filename, interface_list)


if __name__ == "__main__":
    _main()
