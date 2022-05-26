# ----------------------------------------------------------------------
# Vendor: UTST http://www.ecitele.com/
# OS:     ONU
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "UTST.ONU"

    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    command_super = b"enable"
    pattern_unprivileged_prompt = rb"^ONU208i#|ONU2004>"
    pattern_prompt = rb"^ONU208i\(enable\)|ONU2004(?:i#|#)"

    # pattern_prompt = r"^Select menu option.*:"
    # pattern_more = [
    #    (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    #    (r"press <SPACE> to continue or <ENTER> to quit", "               \n"),
    # ]
    command_exit = "logout"

    matchers = {
        "is_platform_onu208": {"platform": {"$regex": r"ONU208"}},
        "is_version_2_0_3_6": {"version": {"$regex": r"2.0.3.6"}},
    }
