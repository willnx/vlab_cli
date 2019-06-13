# -*- coding: UTF-8 -*-
"""Functions for converting something into some other format"""
import time


def epoch_to_date(epoch):
    """Convert an Epoch time to a human-friendly date format

    :Returns: String

    :param epoch: The Epoch value to convert
    :type epoch: Integer
    """
    return time.strftime('%m/%d/%Y %H:%M', time.gmtime(epoch))
