# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## HW:     7302/7330
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7302"
    pattern_prompt = r"^leg:.+#"
    command_save_config = "admin software-mngt shub database save"
    command_exit = "logout"
