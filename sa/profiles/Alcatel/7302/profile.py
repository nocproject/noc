# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     7302/7330
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from typing import Tuple

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.7302"
    pattern_prompt = rb"^(?:typ:|leg:|)\S+(?:>|#)"
    pattern_syntax_error = rb"invalid token"
    pattern_more = [(rb"Press <space>\(page\)/<enter>\(line\)/q\(quit\) to continue...", b" ")]
    pattern_operation_error = rb"Internal processing error"
    command_save_config = "admin software-mngt shub database save"
    command_exit = "logout"
    # exclude rotating dash
    rogue_chars = [re.compile(rb"[\/\|\\\- ]\\x1b\[1D"), b"\r"]

    matchers = {
        "is_telnet_problem": {"version": {"$regex": r"32\.\d+$"}},
    }

    @staticmethod
    def get_slot(slot_id: int) -> Tuple[int, int, int]:
        rack = slot_id >> 12
        shelf = (slot_id >> 8) & 0xF
        slot = slot_id & 0x00FF
        return rack, shelf, slot
