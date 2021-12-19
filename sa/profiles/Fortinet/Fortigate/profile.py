# ---------------------------------------------------------------------
# Vendor: Fortinet
# OS:     FortiOS v4.X
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Fortinet.Fortigate"

    pattern_more = [(rb"^--More--", b" ")]
    pattern_prompt = r"b^\S+\ [#\$]"
