# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXDSL531
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL531"

    pattern_username = rb"Login name:"
    pattern_prompt = rb"^>"
    config_volatile = ["<entry1 sessionID=.+?/>"]
