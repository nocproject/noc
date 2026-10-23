# ---------------------------------------------------------------------
# Vendor: Aruba
# OS:     ArubaOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Aruba.ArubaOS"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = rb"% Parse error"
    command_super = b"enable"
    pattern_more = [(rb"--More-- \(q\) quit \(u\) pageup \(/\) search \(n\) repeat", b" ")]
    rogue_chars = [re.compile(rb"\r\s+\r"), b"\r"]
