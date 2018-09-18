#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Enables building an MSI of the vLab CLI
"""

from setuptools import setup, find_packages

from cx_Freeze import setup, Executable
from vlab_cli import version

packages = ['pkg_resources', 'jwt', 'idna', 'vlab_cli']
bdist_msi_options = {'add_to_path': True, 'install-icon': 'vlab_icon.ico'}

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
      install_requires=['click', 'pyjwt', 'requests', 'tabulate', 'cryptography', 'colorama'],
      executables = [Executable('vlab', base=None, icon='vlab_icon.ico')],
      options = {'build_exe' : {'packages' : packages},
                 'build_msi' : bdist_msi_options},
      )
