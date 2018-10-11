# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# LLDP protocol constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Chassis subtypes
LLDP_CHASSIS_SUBTYPE_CHASSIS_COMPONENT = 1
LLDP_CHASSIS_SUBTYPE_INTERFACE_ALIAS = 2
LLDP_CHASSIS_SUBTYPE_PORT_COMPONENT = 3
LLDP_CHASSIS_SUBTYPE_MAC = 4
LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS = 5
LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME = 6
LLDP_CHASSIS_SUBTYPE_LOCAL = 7

# Port subtypes
LLDP_PORT_SUBTYPE_ALIAS = 1
LLDP_PORT_SUBTYPE_COMPONENT = 2
LLDP_PORT_SUBTYPE_MAC = 3
LLDP_PORT_SUBTYPE_NETWORK_ADDRESS = 4
LLDP_PORT_SUBTYPE_NAME = 5
LLDP_PORT_SUBTYPE_AGENT_CIRCUIT_ID = 6
LLDP_PORT_SUBTYPE_LOCAL = 7
LLDP_PORT_SUBTYPE_UNSPECIFIED = 128

# Capabilities bits
LLDP_CAP_OTHER = 1
LLDP_CAP_REPEATER = 2
LLDP_CAP_BRIDGE = 4
LLDP_CAP_WLAN_ACCESS_POINT = 8
LLDP_CAP_ROUTER = 16
LLDP_CAP_TELEPHONE = 32
LLDP_CAP_DOCSIS_CABLE_DEVICE = 64
LLDP_CAP_STATION_ONLY = 128

# Capabilities names
LLDP_CAP_NAMES = {
    LLDP_CAP_OTHER: "other",
    LLDP_CAP_REPEATER: "repeater",
    LLDP_CAP_BRIDGE: "bridge",
    LLDP_CAP_WLAN_ACCESS_POINT: "wap",
    LLDP_CAP_ROUTER: "router",
    LLDP_CAP_TELEPHONE: "phone",
    LLDP_CAP_DOCSIS_CABLE_DEVICE: "docsis-cable-device",
    LLDP_CAP_STATION_ONLY: "station-only"
}


def lldp_caps_to_bits(caps, caps_map):
    """
    Convert list of LLDP capabilities names to integer,
    suitable to IGetLLDPNeighbors remote_capabilities

    :param caps: List of LLDP capabilities names
    :param caps_map: name -> LLDP_CAP_* mapping. Name in lowercase
    :return: IGetLLDPNeighbors.remote_capabilities
    """
    r = 0
    for cap in caps:
        cv = caps_map.get(cap.lower())
        if cv is not None:
            r += cv
    return r


def lldp_bits_to_caps(bits):
    """
    Convert capabilities bits to canonical names
    :param bits: Integer of bits
    :return: List of names
    """
    r = []
    for i in range(8):
        bv = 1 << i
        if bits & bv:
            r += [LLDP_CAP_NAMES[bv]]
    return r
