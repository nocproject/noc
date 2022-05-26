# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DCN.DCWS"

    pattern_more = [(rb"^ --More-- ", b"\n")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = b"enable"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*#"
    command_submit = b"\n"
    command_exit = "exit"

    matchers = {"is_platform_dcws": {"platform": {"$regex": r"^DCWS.+"}}}
