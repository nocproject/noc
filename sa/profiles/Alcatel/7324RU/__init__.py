# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## HW:     7324 RU
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7324RU"
    pattern_prompt = "^\S+>"
    command_save_config = "config save"
    command_exit = "exit"
