# -*- coding; UTF-8 -*-
"""Common proceedures used for clippy interactions"""
from vlab_cli.lib.widgets import typewriter, prompt


def prompt_and_confirm(prompt_msg, confirm_msg):
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
