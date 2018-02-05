# QFX configuration parser

Convert QFX configuration file to some readable formats
for the following analysis.
    :param filename: Juniper QFX configuration file
    :return: Create JSON, TXT, CSV and HTML translated files

# Quickstart

Example of script launch on Linux, Python 3.6:

```bash
$ python jun-parsing.py -f <path to QFX text configuration file>
```
Launch on Windows do the same way

This script works on Python 3.6 only, because it uses a new feature as 'f' string.