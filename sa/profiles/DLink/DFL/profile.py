# ---------------------------------------------------------------------
# Vendor: D-Link
# OS:     DFL
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DFL"

    pattern_syntax_error = rb"Error: Unknown command:"
    pattern_prompt = rb"^(?P<hostname>\S+(:\S+)*):/> "
    pattern_more = [(rb"^---MORE---", b"a")]
    command_exit = "logout"
    config_volatile = ["^%.*?$"]
