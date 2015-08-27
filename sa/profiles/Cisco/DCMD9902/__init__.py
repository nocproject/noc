# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH

class Profile(noc.sa.profiles.Profile):
    name = "Cisco.DCMD9902"
    supported_schemes = [SSH]
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = "^[Pp]assword:"
    pattern_prompt = "^holding+@.*:"
    pattern_syntax_error = r"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_exit = "exit"
    pattern_more = "--More--"
    command_more = "\n"