# ---------------------------------------------------------------------
# Vendor: AcmePacket
# OS:     NetNet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AcmePacket.NetNet"

    rx_mgmt = re.compile(r"wancom\d+")
    rx_media = re.compile(r"s\d+p\d+")

    @classmethod
    def get_interface_type(cls, name):
        if name[:2] == "lo":
            return "loopback"
        if cls.rx_mgmt.match(name):
            return "physical"
        if cls.rx_media.match(name):
            return "physical"
        return "other"
