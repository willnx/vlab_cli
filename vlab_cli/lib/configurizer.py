# -*- coding: UTF-8 -*-
"""
This module is for reading/writing the vLab configuration file.

The vLab CLI uses a very basic INI format, and looks like::

    [SCP]
    agent=winscp
    location=C:\\some\\path\\WinSCP.exe

    [SSH]
    agent=putty
    location=C:\\some\\path\\putty.exe

    [BROWSER]
    agent=firefox
    location=C:\\some\\path\\firefox.exe

    [RDP]
    agent=mstsc
    location=C:\\some\\path\\mstsc.exe

    [CONSOLE]
    agent=vmrc
    location=C:\\some\\path\\vmrc.exe
"""
import os
import platform
import configparser


CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.vlab')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')
CONFIG_SECTIONS = {'SSH', 'RDP', 'BROWSER', 'SCP', 'CONSOLE'}

def _get_platform_progs():
    base = ['chrome', 'firefox', 'vmrc']
    this_os = platform.system().lower()
    if this_os == 'windows':
        base += ['putty', 'mstsc', 'winscp', 'SecureCRT']
    else:
        base += ['gnome-terminal', 'remmina', 'scp']
    return base

SUPPORTED_PROGS = _get_platform_progs()


def get_config():
    """Load vLab CLI config

    :Returns: configparser.ConfigParser or None
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except Exception:
        config = None
    return config


def set_config(info):
    """Save the configuration values to disk. Supplied info must be nested dictionary.

    :Returns: None

    :Raises: ValueError

    :param info: The mapping of sections and it's key/value configs
    :type info: Dictionary
    """
    sections = set(info.keys())
    if not CONFIG_SECTIONS == sections:
        error = 'vLab Config missing section(s): {}'.format(CONFIG_SECTIONS - sections)
        raise ValueError(error)

    config = configparser.ConfigParser()
    for section, values in info.items():
        config[section] = values
    with open(CONFIG_FILE, 'w') as the_file:
        config.write(the_file)


def find_programs():
    """Walk the filesystem to find the software needed for ``vlab connnect``

    :Returns: Dictionary
    """
    this_os = platform.system().lower()
    if this_os == 'windows':
        search_root = 'C:\\'
        support_programs = {'putty.exe', 'mstsc.exe', 'firefox.exe', 'chrome.exe',
                            'winscp.exe', 'securecrt.exe', 'vmrc.exe'}
    else:
        search_root = '/'
        support_programs = {'gnome-terminal', 'remmina', 'firefox', 'chrome',
                            'scp', 'vmrc'}

    found_programs = {}
    for root, dirs, files in os.walk(search_root):
        if '{' in root:
            # Windows 10 VDI clients have paths with braces in them. This collides
            # with how .format works in the connectorizer.py module resulting
            # in a traceback. Better to just avoid paths with braces...
            continue
        for the_file in files:
            if the_file.lower() in support_programs:
                agent = os.path.splitext(the_file)[0] # remove file extension
                location = os.path.join(root, the_file)
                found_programs[agent.lower()] = location
    if this_os == 'windows':
        found_programs['mstsc'] = 'C:\\Windows\\System32\\mstsc.exe'
        found_programs['vmrc'] = 'C:\\Program Files (x86)\\VMware\\VMware Remote Console\\vmrc.exe'
    else:
        found_programs['vmrc'] = '/usr/bin/vmrc'
    return found_programs
