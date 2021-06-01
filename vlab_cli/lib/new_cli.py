# -*- coding: UTF-8 -*-
"""Handles checking for new versions of the CLI"""
import os.path
import subprocess
import urllib.request
from bs4 import BeautifulSoup

from vlab_cli import version
from vlab_cli.lib.api import build_url
from vlab_cli.lib.widgets import prompt
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.widgets import typewriter


def handle_updates(vlab_api, vlab_config, skip_update_check):
    """Check for an updated CLI, and prompt the user to download if available.

    :Returns: None

    :param vlab_api: An established HTTP/S connect to the vLab server
    :type vlab_api: vlab_cli.lib.api.vLabApi

    :param vlab_config: The user's config
    :type vlab_config: configparser.ConfigParser

    :param skip_update_check: A chicken switch to avoid SPAMing power users
    :type skip_update_check: Boolean
    """
    if skip_update_check:
        return
    page = vlab_api.get('https://vlab.emc.com/getting_started.html').content
    soup = BeautifulSoup(page, features="html.parser")
    site_version = ''
    for a in soup.find_all('a', href=True):
        url = a['href']
        package = os.path.basename(url)
        if package.startswith('vlab-cli'):
            # example package name: vlab-cli-2020.5.21-amd64.msi
            site_version = package.split('-')[2]
            break

    current_version = version.__version__
    if site_version and site_version != current_version:
        question = "A new version of vLab CLI is available. Would you like to install it now? [Y/n]"
        answer = prompt(question, boolean=True, boolean_default=True)
        if answer:
            download_url = build_url(vlab_api.server, url)
            typewriter("Downloading latest version...")
            urllib.request.urlretrieve(download_url, r"C:\Windows\Temp\vlab-cli.msi")
            typewriter("Installing latest version. Please follow any prompts on the installer.")
            # This will launch the install in a non-interactive mode.
            subprocess.call(r"msiexec.exe /i C:\Windows\Temp\vlab-cli.msi /qn /passive")
