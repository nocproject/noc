# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     SMG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.SMG"

    # pattern_username = r"^\S+ login: "
    # pattern_prompt = r"^(?P<hostname>\S+)# "
    pattern_prompt = rb"(SMG2016> )|(/[\w/]+ # )"
    command_exit = "exit"
