# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.DSLAM"

    pattern_username = rb"(?<!Last )[Ll]ogin: "
    pattern_more = [(rb"--More-- ", b" "), (rb"\[Yes/press any key for no\]", b"Y")]
    pattern_prompt = (
        rb"(?P<hostname>\S[A-Za-z0-9-_ \:\.\*\'\,\(\)\/\@\#]+)> (?!Command not found|fail to run,)"
    )
    pattern_syntax_error = rb"Command not found|fail to run,"
    pattern_operation_error = (
        rb"ERROR: Can't stat show result|ALARM: Board temperature mount to limit"
    )
    # command_disable_pager = "terminal datadump"
    # command_super = "enable"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"

    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"

    rx_header = re.compile(r"^\-+$")

    def iter_items(self, s):
        def iter_lines(s):
            lines = s.splitlines()
            # Skip until empty line
            if "" in lines:
                i = lines.index("") + 1
            else:
                i = 0
            ll = len(lines) - 1
            while i <= ll:
                line = lines[i]
                line = line.expandtabs()
                yield line.split()
                i += 1

        d = []
        for line in iter_lines(s):
            match = self.rx_header.search(line[0])
            if match:
                continue
            d += [line]
        return d

    matchers = {
        "is_platform_MXA24": {"platform": {"$regex": r"^MXA24"}},
        "is_platform_MXA32": {"platform": {"$regex": r"^MXA32"}},
        "is_platform_MXA64": {"platform": {"$regex": r"^MXA64"}},
    }
