# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     SuperStack3
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3Com.SuperStack3"
    pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    ]
    command_submit = "\r"
    telnet_send_on_connect = "\r"
    convert_mac = BaseProfile.convert_mac_to_dashed

    def convert_interface_name(self, s):
        if not s.startswith("1:"):
            return "1:" + s
        return s

