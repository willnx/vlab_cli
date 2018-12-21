# -*- coding: UTF-8 -*-
"""Help users with the ``vlab connect`` command"""
import platform

from vlab_cli.lib import configurizer
from vlab_cli.lib.clippy.utils import prompt_and_confirm
from vlab_cli.lib.widgets import typewriter, prompt, Spinner


def invoke_bad_missing_config(username, vlab_url):
    """TODO"""
    typewriter("Hi {}, looks like your vLab configuration file has a problem.".format(username))
    typewriter("The file is located at {}".format(configurizer.CONFIG_FILE))
    typewriter("In order to use the 'vlab connect' commands, we'll have to fix it.")
    typewriter("\nYou can manually fix that file by referencing the spec")
    typewriter("in the official documentation located at: {}".format(vlab_url))
    typewriter("Or I can attempt to fix the file right now (by asking you a pile of questions).")
    return prompt("Do you want me to try and fix your config file? [Yes/no]", boolean=True, boolean_default=True)

def invoke_config():
    typewriter("In order for 'vlab connect' to work, you'll need to have a")
    typewriter("browser, an SSH client, and an SCP client installed.")
    typewriter("Based on your OS, I can use the following:")
    typewriter(", ".join(configurizer.SUPPORTED_PROGS))
    if platform.system().lower() == 'windows':
        typewriter("\nNote: mstsc is the default RDP client that comes with Windows")
    typewriter('\nIf you do not have one of the browsers, SSH, and SCP clients installed')
    typewriter("you'll be wasting time by continuing with this config setup.")
    keep_going = prompt("Continue with config setup? [Yes/no]", boolean=True, boolean_default=True)
    if not keep_going:
        raise RuntimeError("vlab connect prerequisites not met")
    with Spinner('Great! Give me a couple of minutes to find those programs'):
        found_programs = configurizer.find_programs()
        firefox = found_programs.get('firefox', False)
        chrome = found_programs.get('chrome', False)
    if firefox and chrome:
        forget_browser = which_browser()
        found_programs.pop(forget_browser)
    return _make_config(found_programs)


def _make_config(found_programs):
    """Create the config file data structure

    :Returns: Dictionary

    :param found_programs: The result of walking the user's filesystem
    :type found_programs: Dictionary
    """
    new_config = {}
    for agent, prog_path in found_programs.items():
        if agent in ('putty', 'gnome-terminal'):
            new_config['SSH'] = {'agent': agent, 'location': prog_path}
        elif agent in ('firefox', 'chrome'):
            new_config['BROWSER'] = {'agent' : agent, 'location': prog_path}
        elif agent in ('scp', 'winscp'):
            new_config['SCP'] = {'agent': agent, 'location': prog_path}
        elif agent in ('mstsc', 'remmina'):
            new_config['RDP'] = {'agent': agent, 'location': prog_path}
        else:
            raise RuntimeError('Unexpected value for config: {} and {}'.format(agent, prog_path))
    return new_config


def which_browser():
    """If a user has multiple browsers, prompt them about which one to use"""
    typewriter('Looks like you have both Firefox and Chrome installed.')
    choice_question = "Which do you prefer? [chrome/firefox]"
    confirm_question = "Ok, use {}? [yes/No]"
    answer = prompt_and_confirm(choice_question, confirm_question)
    # The answer is which to not use, but people have a hard time with negative questions
    if answer.startswith('f'):
        return 'chrome'
    else:
        return 'firefox'


def invoke_connect_help():
    pass
