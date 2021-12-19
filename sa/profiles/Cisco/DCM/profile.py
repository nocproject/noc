__author__ = "boris"
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.DCM"

    pattern_username = rb"^((?!Last)\S+ login|[Ll]ogin):"
    pattern_prompt = rb"^holding+@.*:"
    pattern_syntax_error = rb"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_exit = "exit"
    pattern_more = [(rb"--More--", b"\n")]
