# -*- coding: UTF-8 -*-
"""
This module centralizes the logging logic of the vLab CLI app
"""
import logging


def get_logger(name, verbose=False):
    """Factory function for obtaining logging object

    :Returns: logging.Logger

    :param name: The name for the log object
    :type name: String

    :param verbose: Set to True for debug logging. Default is False.
    :type verbose: Boolean
    """
    logger = logging.getLogger(__name__)
    if verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s]: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
