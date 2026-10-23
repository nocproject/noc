# ---------------------------------------------------------------------
# Vendor: Protei
# OS:     MAK, MTU, ITG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Protei.MediaGateway"

    command_submit = b"\r"
    pattern_prompt = rb"(^\S+\$|MAK>|MTU>|ITG>)"
