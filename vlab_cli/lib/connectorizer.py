# -*- coding: UTF-8 -*-
"""Logic for opening a specific protocol client"""
import subprocess


class Connectorizer(object):
    """Handles opening the specific protocol client with the correct syntax regardless
    of Platform/OS.

    :param config: The vLab config file
    :type config: configparser.ConfigParser
    """
    def __init__(self, config):
        if config['SSH']['agent'] == 'putty':
            self._ssh_str = '%s -ssh {} -P {}' % config['SSH']['location']
        else:
            self._ssh_str = '%s -- /bin/bash -c "ssh {} -p {}"' % config['SSH']['location']
        # Chrome and Firefox has the same syntax! :D
        self._https_str = '%s --new-window https://{}:{}' % config['BROWSER']['location']
        if config['SCP']['agent'] == 'winscp':
            self._scp_str = '%s scp://{}:{}' % config['SCP']['location']
            self._scp_open = True
        else:
            self._scp_str = 'scp -P {} USER@{} FILE1 FILE2'
            self._scp_open = False
        if config['RDP']['agent'] == 'mstsc':
            self._rdp_str = '%s /v:{}:{} /w:1920 /h:1080' % config['RDP']['location']
        else:
            self._rdp_str = '%s --server {}:{}' % config['RDP']['location']

    def ssh(self, ip_addr, port):
        """Open a session via SSH in a new client"""
        syntax = self._ssh_str.format(ip_addr, port)
        subprocess.Popen(syntax.split(' '))

    def https(self, ip_addr, port, url=None):
        """Open a session via HTTPS in a new client"""
        if url:
            url = url[8:] # strip of redundant https://
            syntax = self._https_str.format(url, '')
            syntax = syntax[:-1] # strip off tailing :
        else:
            syntax = self._https_str.format(ip_addr, port)
        subprocess.Popen(syntax.split(' '))

    def rdp(self, ip_addr, port):
        """Open a session via RDP in a new client"""
        syntax = self._rdp_str.format(ip_addr, port)
        subprocess.Popen(syntax.split(' '))

    def scp(self, ip_addr, port):
        """Open a session via SCP in a new client"""
        syntax = self._scp_str.format(ip_addr, port)
        if self._scp_open:
            subprocess.Popen(syntax.split(' '))
        else:
            print('SCP syntax: {}'.format(syntax))
