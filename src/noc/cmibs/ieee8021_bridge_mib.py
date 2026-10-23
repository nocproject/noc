# ----------------------------------------------------------------------
# IEEE8021-BRIDGE-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "IEEE8021-BRIDGE-MIB"

# Metadata
LAST_UPDATED = "2012-08-10"
COMPILED = "2024-12-27"

# MIB Data: name -> oid
MIB = {
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeMib": "1.3.111.2.802.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeNotifications": "1.3.111.2.802.1.1.2.0",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeObjects": "1.3.111.2.802.1.1.2.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBase": "1.3.111.2.802.1.1.2.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseTable": "1.3.111.2.802.1.1.2.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseEntry": "1.3.111.2.802.1.1.2.1.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseComponentId": "1.3.111.2.802.1.1.2.1.1.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseBridgeAddress": "1.3.111.2.802.1.1.2.1.1.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseNumPorts": "1.3.111.2.802.1.1.2.1.1.1.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseComponentType": "1.3.111.2.802.1.1.2.1.1.1.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseDeviceCapabilities": "1.3.111.2.802.1.1.2.1.1.1.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseTrafficClassesEnabled": "1.3.111.2.802.1.1.2.1.1.1.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseMmrpEnabledStatus": "1.3.111.2.802.1.1.2.1.1.1.1.7",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseRowStatus": "1.3.111.2.802.1.1.2.1.1.1.1.8",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortTable": "1.3.111.2.802.1.1.2.1.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortEntry": "1.3.111.2.802.1.1.2.1.1.4.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortComponentId": "1.3.111.2.802.1.1.2.1.1.4.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePort": "1.3.111.2.802.1.1.2.1.1.4.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortIfIndex": "1.3.111.2.802.1.1.2.1.1.4.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortDelayExceededDiscards": "1.3.111.2.802.1.1.2.1.1.4.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortMtuExceededDiscards": "1.3.111.2.802.1.1.2.1.1.4.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortCapabilities": "1.3.111.2.802.1.1.2.1.1.4.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortTypeCapabilities": "1.3.111.2.802.1.1.2.1.1.4.1.7",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortType": "1.3.111.2.802.1.1.2.1.1.4.1.8",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortExternal": "1.3.111.2.802.1.1.2.1.1.4.1.9",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortAdminPointToPoint": "1.3.111.2.802.1.1.2.1.1.4.1.10",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortOperPointToPoint": "1.3.111.2.802.1.1.2.1.1.4.1.11",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortName": "1.3.111.2.802.1.1.2.1.1.4.1.12",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfToPortTable": "1.3.111.2.802.1.1.2.1.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfToPortEntry": "1.3.111.2.802.1.1.2.1.1.5.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfIndexComponentId": "1.3.111.2.802.1.1.2.1.1.5.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfIndexPort": "1.3.111.2.802.1.1.2.1.1.5.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortTable": "1.3.111.2.802.1.1.2.1.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortEntry": "1.3.111.2.802.1.1.2.1.1.6.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPort": "1.3.111.2.802.1.1.2.1.1.6.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortIfIndex": "1.3.111.2.802.1.1.2.1.1.6.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyMacAddress": "1.3.111.2.802.1.1.2.1.1.6.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortToComponentId": "1.3.111.2.802.1.1.2.1.1.6.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortToInternalPort": "1.3.111.2.802.1.1.2.1.1.6.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTp": "1.3.111.2.802.1.1.2.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortTable": "1.3.111.2.802.1.1.2.1.2.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortEntry": "1.3.111.2.802.1.1.2.1.2.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortComponentId": "1.3.111.2.802.1.1.2.1.2.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPort": "1.3.111.2.802.1.1.2.1.2.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortMaxInfo": "1.3.111.2.802.1.1.2.1.2.1.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortInFrames": "1.3.111.2.802.1.1.2.1.2.1.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortOutFrames": "1.3.111.2.802.1.1.2.1.2.1.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortInDiscards": "1.3.111.2.802.1.1.2.1.2.1.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePriority": "1.3.111.2.802.1.1.2.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortPriorityTable": "1.3.111.2.802.1.1.2.1.3.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortPriorityEntry": "1.3.111.2.802.1.1.2.1.3.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDefaultUserPriority": "1.3.111.2.802.1.1.2.1.3.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortNumTrafficClasses": "1.3.111.2.802.1.1.2.1.3.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortPriorityCodePointSelection": "1.3.111.2.802.1.1.2.1.3.1.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortUseDEI": "1.3.111.2.802.1.1.2.1.3.1.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortRequireDropEncoding": "1.3.111.2.802.1.1.2.1.3.1.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortServiceAccessPrioritySelection": "1.3.111.2.802.1.1.2.1.3.1.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeUserPriorityRegenTable": "1.3.111.2.802.1.1.2.1.3.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeUserPriorityRegenEntry": "1.3.111.2.802.1.1.2.1.3.2.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeUserPriority": "1.3.111.2.802.1.1.2.1.3.2.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeRegenUserPriority": "1.3.111.2.802.1.1.2.1.3.2.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTrafficClassTable": "1.3.111.2.802.1.1.2.1.3.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTrafficClassEntry": "1.3.111.2.802.1.1.2.1.3.3.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTrafficClassPriority": "1.3.111.2.802.1.1.2.1.3.3.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeTrafficClass": "1.3.111.2.802.1.1.2.1.3.3.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortOutboundAccessPriorityTable": "1.3.111.2.802.1.1.2.1.3.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortOutboundAccessPriorityEntry": "1.3.111.2.802.1.1.2.1.3.4.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortOutboundAccessPriority": "1.3.111.2.802.1.1.2.1.3.4.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingTable": "1.3.111.2.802.1.1.2.1.3.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingEntry": "1.3.111.2.802.1.1.2.1.3.5.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingComponentId": "1.3.111.2.802.1.1.2.1.3.5.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPortNum": "1.3.111.2.802.1.1.2.1.3.5.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPriorityCodePointRow": "1.3.111.2.802.1.1.2.1.3.5.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPriorityCodePoint": "1.3.111.2.802.1.1.2.1.3.5.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPriority": "1.3.111.2.802.1.1.2.1.3.5.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingDropEligible": "1.3.111.2.802.1.1.2.1.3.5.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingTable": "1.3.111.2.802.1.1.2.1.3.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingEntry": "1.3.111.2.802.1.1.2.1.3.6.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingComponentId": "1.3.111.2.802.1.1.2.1.3.6.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPortNum": "1.3.111.2.802.1.1.2.1.3.6.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPriorityCodePointRow": "1.3.111.2.802.1.1.2.1.3.6.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPriorityCodePoint": "1.3.111.2.802.1.1.2.1.3.6.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingDropEligible": "1.3.111.2.802.1.1.2.1.3.6.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPriority": "1.3.111.2.802.1.1.2.1.3.6.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityTable": "1.3.111.2.802.1.1.2.1.3.7",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityEntry": "1.3.111.2.802.1.1.2.1.3.7.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityComponentId": "1.3.111.2.802.1.1.2.1.3.7.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityPortNum": "1.3.111.2.802.1.1.2.1.3.7.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityReceived": "1.3.111.2.802.1.1.2.1.3.7.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityValue": "1.3.111.2.802.1.1.2.1.3.7.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeMrp": "1.3.111.2.802.1.1.2.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMrpTable": "1.3.111.2.802.1.1.2.1.4.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMrpEntry": "1.3.111.2.802.1.1.2.1.4.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMrpJoinTime": "1.3.111.2.802.1.1.2.1.4.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMrpLeaveTime": "1.3.111.2.802.1.1.2.1.4.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMrpLeaveAllTime": "1.3.111.2.802.1.1.2.1.4.1.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeMmrp": "1.3.111.2.802.1.1.2.1.5",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpTable": "1.3.111.2.802.1.1.2.1.5.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpEntry": "1.3.111.2.802.1.1.2.1.5.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpEnabledStatus": "1.3.111.2.802.1.1.2.1.5.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpFailedRegistrations": "1.3.111.2.802.1.1.2.1.5.1.1.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpLastPduOrigin": "1.3.111.2.802.1.1.2.1.5.1.1.3",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgePortRestrictedGroupRegistration": "1.3.111.2.802.1.1.2.1.5.1.1.4",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeInternalLan": "1.3.111.2.802.1.1.2.1.6",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeILanIfTable": "1.3.111.2.802.1.1.2.1.6.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeILanIfEntry": "1.3.111.2.802.1.1.2.1.6.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeILanIfRowStatus": "1.3.111.2.802.1.1.2.1.6.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeDot1d": "1.3.111.2.802.1.1.2.1.7",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeDot1dPortTable": "1.3.111.2.802.1.1.2.1.7.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeDot1dPortEntry": "1.3.111.2.802.1.1.2.1.7.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeDot1dPortRowStatus": "1.3.111.2.802.1.1.2.1.7.1.1.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeConformance": "1.3.111.2.802.1.1.2.2",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeCompliances": "1.3.111.2.802.1.1.2.2.1",
    "IEEE8021-BRIDGE-MIB::ieee8021BridgeGroups": "1.3.111.2.802.1.1.2.2.2",
}

DISPLAY_HINTS = {
    "1.3.111.2.802.1.1.2.1.1.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseComponentId
    "1.3.111.2.802.1.1.2.1.1.1.1.2": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseBridgeAddress
    "1.3.111.2.802.1.1.2.1.1.4.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortComponentId
    "1.3.111.2.802.1.1.2.1.1.4.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePort
    "1.3.111.2.802.1.1.2.1.1.4.1.12": (
        "OctetString",
        "255t",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBasePortName
    "1.3.111.2.802.1.1.2.1.1.5.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfIndexComponentId
    "1.3.111.2.802.1.1.2.1.1.5.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeBaseIfIndexPort
    "1.3.111.2.802.1.1.2.1.1.6.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPort
    "1.3.111.2.802.1.1.2.1.1.6.1.3": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePhyMacAddress
    "1.3.111.2.802.1.1.2.1.1.6.1.4": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortToComponentId
    "1.3.111.2.802.1.1.2.1.1.6.1.5": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePhyPortToInternalPort
    "1.3.111.2.802.1.1.2.1.2.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPortComponentId
    "1.3.111.2.802.1.1.2.1.2.1.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeTpPort
    "1.3.111.2.802.1.1.2.1.3.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortDefaultUserPriority
    "1.3.111.2.802.1.1.2.1.3.2.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeUserPriority
    "1.3.111.2.802.1.1.2.1.3.2.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeRegenUserPriority
    "1.3.111.2.802.1.1.2.1.3.3.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeTrafficClassPriority
    "1.3.111.2.802.1.1.2.1.3.4.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortOutboundAccessPriority
    "1.3.111.2.802.1.1.2.1.3.5.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingComponentId
    "1.3.111.2.802.1.1.2.1.3.5.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPortNum
    "1.3.111.2.802.1.1.2.1.3.5.1.5": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortDecodingPriority
    "1.3.111.2.802.1.1.2.1.3.6.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingComponentId
    "1.3.111.2.802.1.1.2.1.3.6.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPortNum
    "1.3.111.2.802.1.1.2.1.3.6.1.6": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortEncodingPriority
    "1.3.111.2.802.1.1.2.1.3.7.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityComponentId
    "1.3.111.2.802.1.1.2.1.3.7.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityPortNum
    "1.3.111.2.802.1.1.2.1.3.7.1.3": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityReceived
    "1.3.111.2.802.1.1.2.1.3.7.1.4": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgeServiceAccessPriorityValue
    "1.3.111.2.802.1.1.2.1.5.1.1.3": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-BRIDGE-MIB::ieee8021BridgePortMmrpLastPduOrigin
}
