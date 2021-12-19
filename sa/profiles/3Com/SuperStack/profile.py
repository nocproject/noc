# ----------------------------------------------------------------------
# Vendor: 3Com
# OS:     SuperStack
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3Com.SuperStack"
    pattern_prompt = rb"^Select menu option.*:"
    pattern_more = [(rb"Enter <CR> for more or 'q' to quit--:", b"\r")]
    command_submit = "\r"
    telnet_send_on_connect = b"\r"
    convert_mac = BaseProfile.convert_mac_to_dashed
