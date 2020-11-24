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
            raise UsageError("CLI flag '--{}' is required".format(self.name.replace('_', '-')))
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


class MultiValue(Option):
    """Pass one or more values to an option. (i.e. nargs=*)"""
    def __init__(self, *args, **kwargs):
        self.save_other_options = kwargs.pop('save_other_options', True)
        nargs = kwargs.pop('nargs', -1)
        assert nargs == -1, 'nargs, if set, must be -1 not {}'.format(nargs)
        super(MultiValue, self).__init__(*args, **kwargs)
        self._previous_parser_process = None
        self._eat_all_parser = None

    def add_to_parser(self, parser, ctx):

        def parser_process(value, state):
            # method to hook to the parser.process
            done = False
            value = [value]
            if self.save_other_options:
                # grab everything up to the next option
                while state.rargs and not done:
                    for prefix in self._eat_all_parser.prefixes:
                        if state.rargs[0].startswith(prefix):
                            done = True
                    if not done:
                        value.append(state.rargs.pop(0))
            else:
                # grab everything remaining
                value += state.rargs
                state.rargs[:] = []
            value = tuple(value)

            # call the actual process
            self._previous_parser_process(value, state)

        retval = super(MultiValue, self).add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._eat_all_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break
        return retval
