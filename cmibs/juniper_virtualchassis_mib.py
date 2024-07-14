# ----------------------------------------------------------------------
# JUNIPER-VIRTUALCHASSIS-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "JUNIPER-VIRTUALCHASSIS-MIB"

# Metadata
LAST_UPDATED = "2024-06-27"
COMPILED = "2024-06-27"

# MIB Data: name -> oid
MIB = {
    "JUNIPER-EX-SMI::jnxExMibRoot": "1.3.6.1.4.1.2636.3.40",
    "JUNIPER-EX-SMI::jnxExSwitching": "1.3.6.1.4.1.2636.3.40.1",
    "JUNIPER-EX-SMI::jnxExVirtualChassis": "1.3.6.1.4.1.2636.3.40.1.4",
    "JUNIPER-SMI::jnxMibs": "1.3.6.1.4.1.2636.3",
    "JUNIPER-SMI::juniperMIB": "1.3.6.1.4.1.2636",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVccpMemberDown": "1.3.6.1.4.1.2636.4.14.0.4",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVccpMemberUp": "1.3.6.1.4.1.2636.4.14.0.3",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVccpNotificationsPrefix": "1.3.6.1.4.1.2636.4.14.0",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVccpPortDown": "1.3.6.1.4.1.2636.4.14.0.2",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVccpPortUp": "1.3.6.1.4.1.2636.4.14.0.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisFpcId": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberAlias": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.10",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberEntry": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberFabricMode": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.11",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberId": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberLocation": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.9",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberMacAddBase": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.4",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberMIB": "1.3.6.1.4.1.2636.3.40.1.4.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberMixedMode": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.12",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberModel": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.8",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberPriority": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.6",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberRole": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.3",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberSerialnumber": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.2",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberSWVersion": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.5",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberTable": "1.3.6.1.4.1.2636.3.40.1.4.1.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisMemberUptime": "1.3.6.1.4.1.2636.3.40.1.4.1.1.1.7",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortAdminStatus": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.3",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortCarrierTrans": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.15",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortCollisions": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.18",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortEntry": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInCRCAlignErrors": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.16",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInMcasts": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.9",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInOctets": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.7",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInOctets1secRate": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.13",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInPkts": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.5",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortInPkts1secRate": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.11",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortName": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.2",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOperStatus": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.4",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOutMcasts": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.10",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOutOctets": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.8",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOutOctets1secRate": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.14",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOutPkts": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.6",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortOutPkts1secRate": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.12",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortTable": "1.3.6.1.4.1.2636.3.40.1.4.1.2",
    "JUNIPER-VIRTUALCHASSIS-MIB::jnxVirtualChassisPortUndersizePkts": "1.3.6.1.4.1.2636.3.40.1.4.1.2.1.17",
    "RFC1155-SMI::dod": "1.3.6",
    "RFC1155-SMI::enterprises": "1.3.6.1.4.1",
    "RFC1155-SMI::internet": "1.3.6.1",
    "RFC1155-SMI::iso": "1",
    "RFC1155-SMI::org": "1.3",
    "RFC1155-SMI::private": "1.3.6.1.4",
}

DISPLAY_HINTS = {}
