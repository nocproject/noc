# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Siklu
# OS:     EH
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Siklu.EH"
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\"\,\(\)\/]+)?>"
    command_submit = "\r"

    def cleaned_input(self, input):
        rx_strip_cmd_repeat = re.compile(
            r'.+\x1b\[\d+G\r?\n(.*)',
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            re.MULTILINE | re.DOTALL)
        match = rx_strip_cmd_repeat.search(input)
        if match:
            input = match.group(1)
        input = super(Profile, self).cleaned_input(input)
<<<<<<< HEAD
        return input

    def convert_interface_name(self, s):
        if s.lower().startswith("eth"):
            return "eth%s" % s[3:].strip()
        else:
            return s.lower()
=======
        print "<<<<<<<<<<<<<<<<<<<<<<<< %r" % input
        return input
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
