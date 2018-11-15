# -*- coding: UTF-8 -*-
"""
This module helps walk users through providing correct input to the CLI
"""
from time import sleep

from vlab_cli.lib.widgets import typewriter, prompt


def _prompt_and_confirm(prompt_msg, confirm_msg):
    """Ask a question, and confirm the response

    :Returns: String

    :param prompt_msg: The question to ask the user.
    :type prompt_msg: String

    :param comfirm_msg: The question to ask to ensure the response is OK.
    :param confirm_msg: String
    """
    prompt_answer = prompt(prompt_msg)
    answer_ok = prompt(confirm_msg.format(prompt_answer), boolean=True)
    while not answer_ok:
        prompt_answer = prompt(prompt_msg)
        answer_ok = prompt(confirm_msg.format(prompt_answer), boolean=True)
    return prompt_answer


def invoke_onefs_clippy(username, cluster_name, version, external_ip_range, node_count, skip_config):
    """Gives some guidance to new(er) users on how to deploy a OneFS cluster

    :Returns: Tuple
    """
    typewriter("\nHi {}! Looks like you're trying to make a OneFS cluster.".format(username))
    sleep(0.5)
    typewriter("To do that, I'm going to need some more information.\n")
    typewriter("You can avoid this prompt in the future by suppling values for the")
    typewriter("--name, --image, and --external-ip-range arguments\n")
    sleep(0.5)
    keep_going = prompt("Do you want me to continue prompting you for this information now? [yes/no]", boolean=True)
    if not keep_going:
        return cluster_name, version, external_ip_range, keep_going
    typewriter("\nGreat!")
    typewriter("I'll help walk you thought the deployment this time.")
    typewriter("Make sure to supply those arguments in the future.")
    typewriter("If you find I keep prompting you for this information,")
    typewriter("you should ask a vLab admin for some help because you're doing it \"the hard way.\"\n")
    if not cluster_name:
        new_cluster_question = "So, what would you like to name your cluster?"
        new_cluster_confirm = "Your new cluster will be named {}, OK? [yes/no]"
        cluster_name = _prompt_and_confirm(new_cluster_question, new_cluster_confirm)
    if not version:
        typewriter("\nOK, now I need to know the version of OneFS to create.")
        typewriter("\nProtip: You can list all available versions in the future with the command:", indent=True)
        typewriter("        vlab show onefs --images", indent=True)
        typewriter("\nGenerally speaking, all released versions of OneFS newer than 8.0.0.0")
        typewriter("are available.")
        version = _get_version()
    if (not external_ip_range) and (not skip_config):
        typewriter('\nYour new cluster will need some external IPs configured.')
        typewriter('The syntax for the --external-ip-range argument is:')
        typewriter('--external-ip-range 1.2.3.4 1.2.3.5', indent=True)
        typewriter('just replace those example IPs with the actual ones you want to use.')
        typewriter('Most OneFS clusters have 1 IP for each node, and you are')
        typewriter('deploying {} node(s).'.format(node_count))
        external_ip_range = _get_ext_ips()
    return cluster_name, version, external_ip_range, not keep_going


def _get_version():
    """A cheeky interaction to get the correct version of OneFS to create

    :Returns: String
    """
    new_version_question = "Now, what version would you like?"
    new_version_ok = "Deploy OneFS {}, correct? [yes/no]"
    answer = prompt(new_version_question)
    if answer.strip() == 'vlab show onefs --images':
        typewriter("When I said \"you can run [that] command in the future\", I meant a much later future ;)")
        typewriter("Like, outside of me walking you through this OneFS deployment.")
        ok = False
    else:
        ok = prompt(new_version_ok.format(answer), boolean=True)
    if not ok:
        answer = _prompt_and_confirm(new_version_question, new_version_ok)
    return answer


def _get_ext_ips():
    """Ensures the supplied IPs are sane

    :Returns: Tuple
    """
    question = "With the syntax of --external-ip-range in mind, what range of IPs do you want to use?"
    answer = prompt(question)
    sanitized, ok = _check_ip_answer(answer)
    if not ok:
        typewriter('Invalid value of {} supplied'.format(answer))
        typewriter('Remember, supply two IPv4 addresses.')
        typewriter('Example: 192.168.1.20 192.168.1.25')
        while not ok:
            answer = prompt(question)
            sanitized, ok = _check_ip_answer(answer)
            if not ok:
                typewriter('Invalid value of {} supplied'.format(answer))
    return sanitized

def _check_ip_answer(answer):
    """Validate the user's answer about "which IPS to use"

    :Returns: Tuple
    """
    ok = True
    sanitized = tuple()
    try:
        high, low = answer.split()
    except Exception:
        ok = False
    else:
        high = high.strip()
        low = low.strip()
        if not (_is_ip(high) and _is_ip(low)):
            ok = False
        else:
            sanitized = (high, low)
    return sanitized, ok


def _is_ip(ipaddr):
    """Validates the the input looks like an IPv4 address.

    :Returns: Boolean

    :param ipaddr: The value to test
    :type ipaddr: String
    """
    ok = True
    count = 0
    for octet in ipaddr.split('.'):
        count += 1
        try:
            int(octet)
        except Exception:
            ok = False
            break
    if ok:
        if count != 4:
            ok = False
    return ok
