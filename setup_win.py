#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Enables building an MSI of the vLab CLI
"""
import sys
from setuptools import setup, find_packages

from cx_Freeze import setup, Executable
from vlab_cli import version

packages = ['pkg_resources', 'jwt', 'idna', 'vlab_cli', 'cryptography', 'cffi']


setup(name="vlab-cli",
      author="Nicholas Willhite",
      version=version.__version__,
      packages=find_packages(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administration',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.5',
      ],
      description="Command Line Interface for vLab",
      long_description=open('README.rst').read(),
      entry_points={'console_scripts' : 'vlab=vlab_cli.vlab:cli'},
      install_requires=['click', 'pyjwt', 'requests', 'tabulate', 'cryptography',
                        'colorama', 'beautifulsoup4'],
      executables = [Executable('vlab', base=None, icon='vlab_icon.ico')],
      options = {'build_exe' : {'packages' : packages},
                 'bdist_msi' : {'upgrade_code': '{4adf8ee9-526b-4b37-a9c3-c46f42de5a53}',
                                'add_to_path': True,
                                'install_icon': 'vlab_icon.ico'}},
      )
