# ----------------------------------------------------------------------
# Vendor: AddPac
# OS:     APOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AddPac.APOS"
    pattern_more = [(rb"^-- more --", b" \n")]
    pattern_prompt = rb"^\S+?#"
    command_submit = b"\r"
    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = "enable"
