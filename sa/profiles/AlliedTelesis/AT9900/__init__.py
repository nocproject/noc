# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Allied Telesis
## OS:     AT9900
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT9900"
    pattern_username = r"^.*\slogin: "
    pattern_more = r"^--More--.*"
    command_more = "c"
    command_submit = "\r"
    command_save_config = "create config=boot1.cfg"
    pattern_prompt = r"^Manager.*>"
    convert_mac = BaseProfile.convert_mac_to_cisco
