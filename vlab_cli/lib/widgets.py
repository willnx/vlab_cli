# -*- coding: UTF-8 -*-
"""
This module contains handy CLI widgets
"""
import sys
import time
import threading

import click


def indenter(text, spaces=4):
    """
    Indent the output a set number of spaces.
    Used mostly for multi-line input as adding a '\t'
    to print will only tab in the first line.

    :param text: The text to indent
    :type text: String

    :param spaces: The number of spaces to indent
    :type spaces: Int

    :Returns: String
    """
    indented = "\n".join(" " * spaces + line for line in text.splitlines())
    return indented


class Spinner:
    """A simple CLI pinwheel, useful when a command takes awhile to complete.

    Turns out, if you just hang the the CLI, humans think "something is wrong"
    and tend to kill the command. Given them a little pinwheel animation keeps
    them from killing the process.

    Example usage
    .. code-block:: python

       from vlab_cli.lib.widgest import Spinner

       with Spinner('My handy message'):
           # do stuff that'll take awhile
       print('All done!')
    """
    def __init__(self, message, delay=0.1):
        self.message = message
        self.busy = False
        self.delay = delay
        self.cursor_chars = '\|/-' # these make a pinwheel
        self.spinner = self.get_spinner_cursor()

    def __enter__(self):
        """Enables use of ``with`` statement"""
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Enables use of the ``with`` statement"""
        self.stop()

    def get_spinner_cursor(self):
        """An iterator that returns the next character in the spinning pinwheel"""
        while True:
            for char in self.cursor_chars:
                yield char

    def spin(self):
        """Writes to stdout to create the CLI pinwheel effect"""
        while self.busy:
            sys.stdout.write('{} {}'.format(self.message, next(self.spinner)))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\r')
            sys.stdout.flush()

    def start(self):
        """Begin the spinning"""
        self.busy = True
        threading.Thread(target=self.spin).start()

    def stop(self):
        """End the spinning"""
        self.busy = False
        time.sleep(self.delay)
        # extra whitespace to overwrite what's left of the spinner
        print('{}  '.format(self.message))
