# -*- coding: UTF-8 -*-
"""
TEMP stuff so the Maestro CLI container will actually do something while we work
on making the literal functionality.
"""
from __future__ import absolute_import, unicode_literals
import random
import termcolor
from sys import stdout
from time import sleep


def colorful_terminal(duration):
    """
    It's like a rainbow in my terminal

    :param duration: How long the fun should last
    :type duration: Integer (seconds)
    """
    colors = ('red', 'green', 'blue', 'yellow')

    def get_block(blocks):
        '''a block of fun! (colors)'''
        group = []
        for i in range(blocks):
            color = random.choice(colors)
            block = termcolor.colored(' ', color, attrs=['reverse'])
            group.append(block)
        return group

    window = 0.0
    while (window < duration):
        stdout.write('\r{0}'.format(''.join(get_block(50))))
        stdout.flush()
        sleep(0.1)
        window += 0.1
    stdout.write("\r{0}".format(' ' * 50))
    stdout.write("\r\n\tYour day just got better!\n\n")
    stdout.flush()

if __name__ == '__main__':
    colorful_terminal(5)
