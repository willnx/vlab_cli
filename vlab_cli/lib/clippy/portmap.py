# -*- coding: UTF-8 -*-
"""Help users choose which protocol to create a port mapping rule for"""
from vlab_cli.lib.clippy.utils import prompt_and_confirm
from vlab_cli.lib.widgets import typewriter, prompt

def invoke_portmap_clippy(username, vm_type, available_protocols):
    """Help the human choose a protocol when creating/deleting a port mapping/fowarding rule.

    :Returns: String

    :param username: The human that needs some assistance
    :type username: String

    :param vm_type: The category of vLab component (i.e. OneFS, InsightIQ, etc)
    :type vm_type: String

    :param available_protocols: The protocols supported for the given vm_type
    :type available_protocols: List
    """
    typewriter("Hi {}, looks like you forgot or provided an invalid protocol".format(username))
    typewriter("of a port mapping/forwarding rule.\n")
    typewriter("Honestly, I don't blame you; I have to look it up which protocols")
    typewriter("are supported by the different components, and I'm a robot!\n")
    typewriter("Looks like the {} component supports these protocols:".format(vm_type))
    typewriter("{}".format(' '.join(available_protocols)))
    choice_question = "\nWhich protocol do you want to use?"
    confirm_question = "Ok, use {}? [yes/No]"
    answer = prompt_and_confirm(choice_question, confirm_question)
    if not answer in available_protocols:
        typewriter('\nerror, does not compute...', newline=False)
        typewriter('\rEhh, I mean that is not a valid option')
        typewriter('Remember your options are:')
        typewriter("{}".format(' '.join(available_protocols)))
        while not answer in available_protocols:
            answer = prompt_and_confirm(choice_question, confirm_question)
    return answer
