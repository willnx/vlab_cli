# -*- coding: UTF-8 -*-
"""Logic for opening a specific protocol client"""
import os.path
import subprocess

import click

from vlab_cli.lib.widgets import printerr


class Connectorizer(object):
    """Handles opening the specific protocol client with the correct syntax regardless
    of Platform/OS.

    :param config: The vLab config file
    :type config: configparser.ConfigParser
    """
    def __init__(self, config, gateway_ip, user='root', password='a'):
        self.config = config
        self._gateway_ip = gateway_ip
        if config['SSH']['agent'] == 'putty':
            self._ssh_str = '%s -ssh {} -P {}' % config['SSH']['location']
        elif config['SSH']['agent'] == 'securecrt':
            self._ssh_str = '%s /SSH2 {} /P {}' % config['SSH']['location']
        elif config['SSH']['agent'] == 'wt':
            self._ssh_str = '%s new-tab ssh %s@{} -p {}' % (config['SSH']['location'], user)
        elif config['SSH']['agent'] == 'gnome-terminal':
            self._ssh_str = '%s -- ssh %s@{} -p {}' % (config['SSH']['location'], user)
        else:
            error = 'Unknown SSH agent: %s' % config['SSH']['agent']
            raise RuntimeError(error)
        # Chrome and Firefox has the same syntax! :D
        self._https_str = '%s --new-window https://{}:{}' % config['BROWSER']['location']

        if config['SCP']['agent'] == 'winscp':
            self._scp_str = '%s scp://%s:%s@{}:{}' % (config['SCP']['location'], user, password)
            self._scp_open = True
        elif config['SCP']['agent'] == 'filezilla':
            self._scp_str = '%s sftp://%s:%s@{}:{}' % (config['SCP']['location'], user, password)
            self._scp_open = True
        else:
            self._scp_str = 'scp -P {} USER@{} FILE1 FILE2'
            self._scp_open = False

        if config['RDP']['agent'] == 'mstsc':
            self._rdp_str = '%s /v:{}:{} /w:1920 /h:1080' % config['RDP']['location']
        else:
            self._rdp_str = '%s --server {}:{}' % config['RDP']['location']
        # VMRC is the same regardless of OS
        self._console_str = '%s vmrc://readonly@vlab.local@vlab-vcenter.emc.com/?moid={}' % config['CONSOLE']['location']


    def ssh(self, port):
        """Open a session via SSH in a new client"""
        syntax = self._ssh_str.format(self._gateway_ip, port)
        self.execute_client(syntax, 'SSH')

    def https(self, port, url='', endpoint=''):
        """Open a session via HTTPS in a new client"""
        if url:
            url = url[8:] # strip of redundant https://
            syntax = self._https_str.format(url, '')
            syntax = syntax[:-1] # strip off tailing :
        elif endpoint:
            syntax = self._https_str.format(self._gateway_ip, port) + endpoint
        else:
            syntax = self._https_str.format(self._gateway_ip, port)
        self.execute_client(syntax, 'Browser')

    def rdp(self, port):
        """Open a session via RDP in a new client"""
        syntax = self._rdp_str.format(self._gateway_ip, port)
        self.execute_client(syntax, 'RDP')

    def scp(self, port):
        """Open a session via SCP in a new client"""
        syntax = self._scp_str.format(self._gateway_ip, port)
        if self._scp_open:
            self.execute_client(syntax, 'SCP')
        else:
            print('SCP syntax: {}'.format(syntax))

    def console(self, vm_moid):
        """Open the console to a VM with VMRC"""
        syntax = self._console_str.format(vm_moid)
        self.execute_client(syntax, 'Console')

    def execute_client(self, syntax, kind):
        """Provides a better error message than subprocess if the exec doesn't exist

        :Returns: None

        :param syntax: The CLI command to execute
        :type syntax: String

        :param kind: The type of client being launched
        :type kind: String
        """
        client_path = self.config[kind.upper()]['location']
        if not exists(client_path):
            printerr('{} client not found at {}'.format(kind, client_path))
            printerr('Please update your $HOME/.vlab/config.ini to resolve')
        else:
            subprocess.Popen(syntax.split(' '))


def exists(path):
    """Because Python on Windows fails for archive links (which are files...)"""
    directory = os.path.dirname(path)
    the_file = os.path.basename(path)
    return the_file in os.listdir(directory)
