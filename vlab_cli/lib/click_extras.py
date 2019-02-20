# -*- coding: UTF-8 -*-
"""
This module provides additional functionality for the click library
"""
from click import command, option, Option, UsageError


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
    """Enables sharing of arbitrary data across the CLI app"""
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            object.__setattr__(self, str(k), v)
