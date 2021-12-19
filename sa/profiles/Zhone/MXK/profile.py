# ---------------------------------------------------------------------
# Vendor: Zhone
# OS:     MXK
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zhone.MXK"

    # pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*[>#]"
    pattern_syntax_error = rb"ERROR: Permission denied."
    pattern_more = [(rb"<SPACE> for next page, <CR> for next line, A for all, Q to quit", b"a")]
