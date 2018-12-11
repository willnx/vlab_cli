# -*- coding: UTF-8 -*-
"""
This module provides additional functionality for the click library
"""
from click import command, option, Option, UsageError, ClickException


class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help_ = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_ + (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


class MandatoryOption(Option):
    """Require a specific flag to be supplied"""
    def __init__(self, *args, **kwargs):
        help_ = kwargs.get('help', '')
        kwargs['help'] = help_ + " [required]"
        super(MandatoryOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.name not in opts:
            raise UsageError("CLI flag '{}' is required".format(self.name))
        return super(MandatoryOption, self).handle_parse_result(ctx, opts, args)


class HiddenOption(Option):
    """Hide this flag in the help page output"""
    def __init__(self, *args, **kwargs):
        self.hidden=True
        super(HiddenOption, self).__init__(*args, **kwargs)

    def get_help_record(self, *args, **kwargs):
        return


class GlobalContext(object):
    """Enables sharing of arbitrary data across the CLI app

    *IMPORTANT* This data should be considered read-only. You cannot rebind
                attributes, but this is Python so you *could* modify the attribute
                value provided it's a mutable data type (i.e. list, dict, etc.).
                Please don't do that, you'll regret it; trust me :D
    """
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            object.__setattr__(self, str(k), v)

    def __setattr__(self, attr, value):
        raise AttributeError("can't set attribute")

    def __delattr__(self, attr):
        raise AttributeError("can't set attribute")


def get_portmap_ip(ips, ip_address):
    """Determines which (if any) IP address to use in a port mapping rule.

    :Returns: String

    :Raises: click.ClickException

    :param ips: The IPs owned/assigned to the VM
    :type ips: List

    :param ip_address: An explicit IP to use, supplied by the user, or None
    :type ip_address: Enum(None, String)
    """
    if not (ip_address is None):
        if not ip_address in ips:
            error = 'Supplied IP is not owned by VM. VM has {}'.format(ips)
            raise ClickException(error)
        else:
            return ip_address
    elif len(ips) == 1:
        return ips[0]
    elif len(ips) > 1:
        error = 'Must supply `--ip-address` when VM has mutiple IPs. Found: {}'.format(ips)
        raise ClickException(error)
    else:
        error = "VM has no IPs. Unable to map a port"
        raise ClickException(error)
