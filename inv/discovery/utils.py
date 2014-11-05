## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from settings import config

##
DISCOVERY_METHODS = [
    "version_inventory",
    "caps_discovery",
    "id_discovery",
    "config_discovery",
    "interface_discovery",
    "asset_discovery",
    "vlan_discovery",
    "lldp_discovery",
    "udld_discovery",
    "bfd_discovery",
    "stp_discovery",
    "cdp_discovery",
    "oam_discovery",
    "rep_discovery",
    "ip_discovery",
    "mac_discovery",
]

ACTIVE_DISCOVERY_METHODS = None


def get_active_discovery_methods():
    """
    Returns a list of active discovery methods
    """
    global ACTIVE_DISCOVERY_METHODS, DISCOVERY_METHODS

    if ACTIVE_DISCOVERY_METHODS is None:
        ACTIVE_DISCOVERY_METHODS = [
            m for m in DISCOVERY_METHODS
            if (config.has_section(m) and
                config.has_option(m, "enabled") and
                config.getboolean(m, "enabled"))
        ]
    return ACTIVE_DISCOVERY_METHODS
