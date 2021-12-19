# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     ZyNOSv2
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.ZyNOSv2"

    pattern_prompt = rb"^\S+?>"
    pattern_more = [(rb"^---MORE---", b" ")]
    enable_cli_session = False
