# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
from noc.core.profile.base import BaseProfile

class Profile(BaseProfile):
    name = "Cisco.DCM"
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_prompt = "^holding+@.*:"
    pattern_syntax_error = r"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_exit = "exit"
    pattern_more = "--More--"
    command_more = "\n"
