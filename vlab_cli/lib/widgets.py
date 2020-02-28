# -*- coding: UTF-8 -*-
"""
This module contains handy CLI widgets
"""
import sys
import time
import random
import string
import threading

import click

NO_SCROLL_OUTPUT = False


def to_timestamp(epoch):
    """Return a human-friendly timestamp

    :Returns: String

    :param epoch: The EPOCH time to convert into a timestamp.
    :type epoch: Integer
    """
    local_time = time.localtime(epoch)
    time_format = '%Y-%m-%d %H:%M:%S %Z'
    time_stamp = time.strftime(time_format, local_time)
    return time_stamp


def prompt(question, boolean=False, boolean_default=False):
    """Ask a user a question.

    :Returns: Boolean or String

    :param question: What to prompt the user about.
    :type question: String

    :param boolean: Set to True if the question has a yes/no answer
    :type boolean: Boolean

    :param boolean_default: Only applies when boolean is True. Defines what is
                            returned if the user simply presses the "enter" key.
    :type boolean_default: Boolean
    """
    typewriter(question, newline=False)
    answer =  input(' ')
    if boolean:
        if answer == '':
            answer = boolean_default
        else:
            answer = True if answer.lower().startswith('y') else False
    return answer

def do_easter_egg(message):
    """This fun little gem purposefully mis-types a message, then fixes it.

    :Returns: None

    :param message: What to (normally) say to the user
    :type message: String
    """
    fun_times = random.randint(1, 1000) == 42
    if fun_times:
        chars = len(message)
        derp_point = int(chars/2)
        derps = max(1, min(3, derp_point / 2))
        for idx, char in enumerate(message):
            if idx == derp_point:
                random_chars = []
                for _ in range(derps):
                    derp_char = random.choice(string.ascii_letters)
                    random_chars.append(derp_char)
                    sys.stdout.write(derp_char)
                    sys.stdout.flush()
                time.sleep(1)
                for backup in reversed(range(derps)):
                    random_chars[backup] = ' '
                    one_less_derp = '{}{}'.format(message[:derp_point], ''.join(random_chars))
                    sys.stdout.write('\r{}'.format(one_less_derp))
                    sys.stdout.flush()
                    time.sleep(0.2)
                sys.stdout.write('\r{}{}'.format(message[:idx], char))
                sys.stdout.flush()
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.05)
    return fun_times


def typewriter(message, newline=True, indent=False):
    """Output a message one character at a time

    The point of this function is to help draw a user's eye to what's being noted
    on the screen. The idea is that the movement will draw their attention, which
    will increase the chances they'll actually read the output.

    :Returns: None

    :param message: The information to print to the terminal
    :type message: String

    :param newline: Automatically insert the newline char after the message
    :type newline: Boolean

    :param indent: Add a few extra spaces before the message
    :type indent: Boolean
    """
    if indent:
        message = indenter(message)
    if NO_SCROLL_OUTPUT:
        sys.stdout.write(message)
        sys.stdout.flush()
    elif do_easter_egg(message):
        pass
    else:
        for idx, char in enumerate(message):
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.05)
    if newline:
        sys.stdout.write('\n')
        sys.stdout.flush()


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
        typewriter(self.message, newline=False)
        sys.stdout.write('\r')
        sys.stdout.flush()
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


def printerr(message):
    """Like 'print()', but writes to stderr"""
    sys.stderr.write('{}\n'.format(message))
    sys.stderr.flush()
