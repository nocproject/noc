# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     7324 RU
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7324RU"
    pattern_prompt = rb"^\S+>"
    pattern_more = [(rb"Press any key to continue, 'e' to exit, 'n' for nopause", b"n")]
    command_save_config = "config save"
    command_exit = "exit"
