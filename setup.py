#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Enables building standard Python vLab CLI distributions
"""
from setuptools import setup, find_packages

from vlab_cli import version


setup(name="vlab-cli",
      author="Nicholas Willhite",
      version=version.__version__,
      packages=find_packages(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administration',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.5',
      ],
      description="Command Line Interface for vLab",
      long_description=open('README.rst').read(),
      entry_points={'console_scripts' : 'vlab=vlab_cli.vlab:cli'},
      install_requires=['click', 'pyjwt', 'requests', 'tabulate', 'cryptography', 'colorama'],
      )
