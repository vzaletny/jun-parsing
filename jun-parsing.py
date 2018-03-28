"""
    Convert QFX configuration file to some readable formats for
    the following analysis
    filename: - Juniper QFX configuration file
    return: Create JSON, TXT, CSV and HTML translated files
"""
import argparse
import json
import re
from tabulate import tabulate
import unicodecsv as csv
import os.path
import pandas as pd


def parse_qfe_config(lines):
    intf_desc = {}
    intfs_list = []
    re_intf_desc = re.compile(r'^set interfaces +(?P<interface>\S+)'
                              r'.*description +(?P<description>\S+)'
                              )
    re_mode = re.compile(r'^set interfaces +(?P<interface>\S+)'
                         r'.*interface-mode +(?P<mode>\S+)'
                         )
    re_vlan = re.compile(r'^set interfaces +(?P<interface>\S+)'
                         r'.*vlan +members +(?P<vlan>[\d+-].+)'
                         )
    re_irb = re.compile(r'^set interfaces +(?P<interface>\S+)'
                        r' +unit (?P<unit>\d+).*description'
                        r' +(?P<description>\S+)'
                        )
    re_irb_ip = re.compile(r'^set interfaces +(?P<interface>\S+)'
                           r' +unit (?P<unit>\d+).*address'
                           r' +(?P<ip>[\d.]+/\d+)'
                           )

    def parse_desc(cfg_line):
        nonlocal intf_desc
        unit = '0'
        if 'irb' in cfg_line:
            irb_match = re_irb.search(cfg_line)
            unit = irb_match.group('unit')
        intf_desc_match = re_intf_desc.search(cfg_line)
        if intf_desc_match:
            intf = intf_desc_match.group('interface')
            if intf != intf_desc.get('interface') or unit != '0':
                if intf_desc:
                    intfs_list.append(intf_desc)
                intf_desc = {
                    'interface': intf_desc_match.group('interface'),
                    'description': intf_desc_match.group('description'),
                    'vlans': '',
                    'unit': unit,
                    'ip': '',
                }

    def parse_intf_mode(cfg_line):
        nonlocal intf_desc
        mode_match = re_mode.search(cfg_line)
        if mode_match:
            intf = mode_match.group('interface')
            if intf == intf_desc.get('interface'):
                intf_desc['mode'] = mode_match.group('mode')

    def parse_vlan_member(cfg_line):
        nonlocal intf_desc
        vlan_match = re_vlan.search(cfg_line)
        if vlan_match:
            intf = vlan_match.group('interface')
            if intf == intf_desc.get('interface'):
                if not intf_desc['vlans']:
                    sep = ''
                else:
                    sep = ','
                intf_desc['vlans'] = \
                    f"{intf_desc['vlans']}{sep}{vlan_match.group('vlan')}"

    def parse_ip_address(cfg_line):
        nonlocal intf_desc
        irb_match = re_irb_ip.search(cfg_line)
        if irb_match:
            intf = irb_match.group('interface')
            unit = irb_match.group('unit')
            if intf == intf_desc.get('interface') \
                    and unit == intf_desc.get('unit'):
                intf_desc['ip'] = irb_match.group('ip')

    for line in lines:
        if 'description' in line:
            parse_desc(line)
        elif 'interface-mode' in line:
            parse_intf_mode(line)
        elif 'vlan members' in line:
            parse_vlan_member(line)
        elif 'family inet address' in line:
            parse_ip_address(line)
    return intfs_list


def load_qfe_file(filename):
    with open(filename, mode='r', encoding='utf-8') as file_handler:
        return file_handler.readlines()


def save_to_txt(filename, intfs_list):
    grid_txt = tabulate(intfs_list, headers='keys', tablefmt='grid')
    with open(f'{filename}.txt', 'w', encoding='utf-8') as file_handler:
        file_handler.write(grid_txt)


def save_to_html(filename, intfs_list):
    html_out = tabulate(intfs_list, headers='keys', tablefmt='html')
    with open(f'{filename}.html', 'w', encoding='utf-8') as file_handler:
        file_handler.write(html_out)


def save_to_json(filename, intfs_list):
    with open(f'{filename}.json', 'w', encoding='utf-8') as file_handler:
        json.dump(intfs_list,
                  file_handler,
                  sort_keys=True,
                  indent=4,
                  ensure_ascii=False
                  )


def save_to_csv(filename, intfs_list):
    with open(f'{filename}.csv', 'wb') as file_handler:
        writer = csv.DictWriter(file_handler,
                                quoting=csv.QUOTE_NONNUMERIC,
                                fieldnames=intfs_list[0],
                                delimiter=';'
                                )
        writer.writeheader()
        writer.writerows(intfs_list)


def save_to_xlsx(filename, intfs_list):
    df = pd.DataFrame(intfs_list)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(path=f'{filename}.xlsx', engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def save_to_files(filename, intfs_list):
    filename = f'{os.path.splitext(filename)[0]}_convert_to_'
    save_to_funcs = [
        save_to_txt,
        save_to_html,
        save_to_json,
        save_to_csv,
        save_to_xlsx,
    ]
    for save_to_func in save_to_funcs:
        save_to_func(filename, intfs_list)


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
        lines = load_qfe_file(filename)
        intfs_list = parse_qfe_config(lines)
        save_to_files(filename, intfs_list)
    except FileNotFoundError:
        exit(f'File {filename} not found')
    except OSError as os_error:
        print(f'I/O error with a {filename} file, something went wrong')
        exit(os_error)


if __name__ == "__main__":
    _main()
