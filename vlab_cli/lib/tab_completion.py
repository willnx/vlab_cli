# -*- coding: UTF-8 -*-
"""Users love being able to jam the TAB key instead of typing"""
import click_completion.core

from vlab_cli.lib.widgets import typewriter


def install_tab_complete_config(for_shell):
    shell, path = click_completion.core.install(shell=for_shell)
    typewriter('Configured tab-completion for {}'.format(shell))
    typewriter('The config file is located at: {}'.format(path))
    typewriter('For tab-completion to work you MUST open a new {} shell'.format(shell))
