# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VPN utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct
# Third-party modules
from csiphash import siphash24

SIPHASH_SEED = b"\x00" * 16


def get_vpn_id(vpn):
    """
    Calculate RFC2685-compatible VPN ID
    :param vpn: Dict containing following keys
        * type - with VPN type ("VRF", "VPLS", "VLL", "EVPN")
        * vpn_id (optional) - given vpn id
        * rd (optional) - VRF RD
        * name (optional) - Local VPN name
        * rt_export (optional) - List of exported route targets (["xx:yy", ..., "xx:yy"]
    :return:
    """
    vpn_id = vpn.get("vpn_id")
    if vpn_id:
        # Already calculated
        return vpn_id.lower()
    # Generate VPN identity fingerprint
    rt_export = vpn.get("rt_export", [])
    if rt_export:
        identity = ":".join(sorted(rt_export))
    elif vpn.get("rd"):
        if vpn["rd"] == "0:0":
            return "0:0"
        identity = vpn["rd"]
    elif vpn.get("name"):
        identity = vpn["name"]
    else:
        raise ValueError("Cannot calculate VPN id")
    identity = "%s:%s" % (vpn["type"], identity)
    # RFC2685 declares VPN ID as <IEEE OUI (3 octets)>:<VPN number (4 octets)
    # Use reserved OUI range 00 00 00 - 00 00 FF to generate
    # So we have 5 octets to fill vpn id
    # Use last 5 octets of siphash 2-4
    i_hash = siphash24(SIPHASH_SEED, str(identity))
    return "%x:%x" % struct.unpack("!BI", i_hash[3:])
