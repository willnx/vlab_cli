# -*- coding: UTF-8 -*-
"""Gives a brief tutorial of how to use vLab"""
import time

import click

from vlab_cli.lib.widgets import typewriter, prompt

VLAB_ASCII = """\
        _           _
       | |         | |
 __   _| |     __ _| |__
 \ \ / / |    / _` | '_ \\
  \ V /| |___| (_| | |_) |
   \_/ |______\__,_|_.__/
"""


def invoke_greeting(username):
    typewriter('Hello {}, welcome to'.format(username))
    for line in VLAB_ASCII.split('\n'):
        print(line)
        time.sleep(0.5)


def invoke_eula():
    typewriter("Before we get started, let's go over the one basic rule with")
    typewriter("using vLab:\n")
    time.sleep(0.6)
    click.secho("\tDon't ruin this for others\n", bold=True)
    time.sleep(1)
    typewriter("It's a simple rule, right? Well, \"they\" (you know, the ominous")
    typewriter("\"they\") say I should provide a bit more detail. So without")
    typewriter("further ado here's a list of things, not limited to, that")
    typewriter("constitutes \"ruining this for others\":\n")
    typewriter("\t* Creating a bot net")
    typewriter("\t* Mining cryptocurrency (ex Bitcoin)")
    typewriter("\t* Running non-work related software in your lab")
    typewriter("\t* Using lab resources for production anything")
    typewriter("\t* Hacking or general maliciousness of any kind\n")
    typewriter("Violating this one very basic rule will result in, but not limited to,")
    typewriter("being banned from using vLab. Please do not be that person who")
    typewriter("\"ruins this for others.\"\n")
    accepts_terms = prompt("Do you understand and agree to follow this one basic rule? [y/N]", boolean=True)
    return accepts_terms


def invoke_tutorial():
    keep_going = prompt('Would you like to go over using the vLab CLI? [Yes/no]', boolean=True, boolean_default=True)
    if not keep_going:
        typewriter("Ok, but don't get angry when I tell you, \"you did it wrong.\" :P\n")
        return
    typewriter('Awesome, I like explaining this sort of thing!\n')

    typewriter('The vLab CLI can be broken down into *commands* and *arguments* (aka flags, aka options).')
    typewriter('An argument always starts with either a dash (-) or a double-dash (--).')
    typewriter('For example, --name is an argument and so is -v\n')

    typewriter('A command just starts with a letter, so if you see no dashes')
    typewriter("just assume it's a command. A command can also have a *subcommand*,")
    typewriter("which is a fancy way to say that \"words can come after words.\"\n")

    typewriter("For example, the command 'vlab init' consist of the base command")
    typewriter("'vlab' followed by the subcommand 'init'.\n")

    typewriter("Now, arguments belong to their specific command (or subcommand).")
    typewriter("This means you cannot mix and match order at the command line.\n")

    typewriter("For instance, an argument of the 'vlab' command is '--verify'")
    typewriter("and the 'init' subcommand has no '--verify' argument.\n")

    typewriter("So if you try to run 'vlab init --verify', I'm going to generate")
    typewriter("an error telling you that \"you did it wrong.\"\n")

    typewriter("Personally, I feel like the hardest part of using a CLI is learning")
    typewriter("\"what's the command for that again...\" (aka command syntax).")
    typewriter("If you remember one thing today, remember that *every command*")
    typewriter("supports the '--help' argument, which will output a little")
    typewriter("help-page noting the valid arguments and subcommands.\n")

    typewriter("I know that using a CLI can be tough at first, especially if you're")
    typewriter("\"from a Windows background\", so don't be surprised if I reach out")
    typewriter("at some point in the future to help with command syntax.\n")


def invoke_init_done_help():
    typewriter("Woot! Your virtual lab is ready to use!\n")
    typewriter("You can use 'vlab create --help' to find out what you can make.")
    typewriter("Replacing the word 'create' with 'delete' or 'show' in that command")
    typewriter("does what you think it does.\n")
    typewriter("Use the command 'vlab power [on/off/restart]' if you need to")
    typewriter("change the power state of a component in your lab.\n")
    typewriter("If you have any questions, the official vLab docs might have your")
    typewriter("answer, or at least how to contact a human.\n")
    typewriter("Thanks for using vLab! :)\n")



if __name__ == '__main__':
    invoke_eula()
    invoke_tutorial()
