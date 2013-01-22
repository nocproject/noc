# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Siklu
## OS:     EH
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH


class Profile(noc.sa.profiles.Profile):
    name = "Siklu.EH"
    supported_schemes = [SSH]
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^\S+?>"
    command_submit = "\r"


    def cleaned_input(self, input):
        print ">>>>>>>>>>>>>>>>>>>>>>>> %r" % input
        rx_strip_cmd_repeat = re.compile(r'.+\x1b\[\d+G\r?\n(.*)',
            re.MULTILINE | re.DOTALL)
        match = rx_strip_cmd_repeat.search(input)
        if match:
            input = match.group(1)
        input = super(Profile, self).cleaned_input(input)
        print "<<<<<<<<<<<<<<<<<<<<<<<< %r" % input
        return input
