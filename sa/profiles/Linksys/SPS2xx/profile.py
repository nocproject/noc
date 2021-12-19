# ---------------------------------------------------------------------
# Vendor: Linksys
# OS:     SPS2xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linksys.SPS2xx"

    pattern_more = [(rb"^More: <space>,  Quit: q, One line: <return>$", b"\r")]
    pattern_unprivileged_prompt = rb"^\S+> "
    pattern_syntax_error = rb"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered)$"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = rb"^\S+# "
