# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     7302/7330
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7302"
    pattern_prompt = r"^(?:typ:|leg:|)\S+(?:>|#)"
    pattern_syntax_error = r"invalid token"
    pattern_more = r"Press <space>\(page\)/<enter>\(line\)/q\(quit\) to continue..."
    command_save_config = "admin software-mngt shub database save"
    command_exit = "logout"
    command_more = " "
