# ----------------------------------------------------------------------
# IEEE8021-Q-BRIDGE-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "IEEE8021-Q-BRIDGE-MIB"

# Metadata
LAST_UPDATED = "2011-12-12"
COMPILED = "2024-12-27"

# MIB Data: name -> oid
MIB = {
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeMib": "1.3.111.2.802.1.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeMibObjects": "1.3.111.2.802.1.1.4.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeBase": "1.3.111.2.802.1.1.4.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTable": "1.3.111.2.802.1.1.4.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEntry": "1.3.111.2.802.1.1.4.1.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeComponentId": "1.3.111.2.802.1.1.4.1.1.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanVersionNumber": "1.3.111.2.802.1.1.4.1.1.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeMaxVlanId": "1.3.111.2.802.1.1.4.1.1.1.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeMaxSupportedVlans": "1.3.111.2.802.1.1.4.1.1.1.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNumVlans": "1.3.111.2.802.1.1.4.1.1.1.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeMvrpEnabledStatus": "1.3.111.2.802.1.1.4.1.1.1.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortTable": "1.3.111.2.802.1.1.4.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortEntry": "1.3.111.2.802.1.1.4.1.1.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortComponentId": "1.3.111.2.802.1.1.4.1.1.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortNumber": "1.3.111.2.802.1.1.4.1.1.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortRowStatus": "1.3.111.2.802.1.1.4.1.1.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTp": "1.3.111.2.802.1.1.4.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbTable": "1.3.111.2.802.1.1.4.1.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbEntry": "1.3.111.2.802.1.1.4.1.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbComponentId": "1.3.111.2.802.1.1.4.1.2.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbId": "1.3.111.2.802.1.1.4.1.2.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbDynamicCount": "1.3.111.2.802.1.1.4.1.2.1.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbLearnedEntryDiscards": "1.3.111.2.802.1.1.4.1.2.1.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbAgingTime": "1.3.111.2.802.1.1.4.1.2.1.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbTable": "1.3.111.2.802.1.1.4.1.2.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbEntry": "1.3.111.2.802.1.1.4.1.2.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbAddress": "1.3.111.2.802.1.1.4.1.2.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbPort": "1.3.111.2.802.1.1.4.1.2.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbStatus": "1.3.111.2.802.1.1.4.1.2.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupTable": "1.3.111.2.802.1.1.4.1.2.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupEntry": "1.3.111.2.802.1.1.4.1.2.3.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupAddress": "1.3.111.2.802.1.1.4.1.2.3.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupEgressPorts": "1.3.111.2.802.1.1.4.1.2.3.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupLearnt": "1.3.111.2.802.1.1.4.1.2.3.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllTable": "1.3.111.2.802.1.1.4.1.2.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllEntry": "1.3.111.2.802.1.1.4.1.2.4.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllVlanIndex": "1.3.111.2.802.1.1.4.1.2.4.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllPorts": "1.3.111.2.802.1.1.4.1.2.4.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllStaticPorts": "1.3.111.2.802.1.1.4.1.2.4.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllForbiddenPorts": "1.3.111.2.802.1.1.4.1.2.4.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredTable": "1.3.111.2.802.1.1.4.1.2.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredEntry": "1.3.111.2.802.1.1.4.1.2.5.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredVlanIndex": "1.3.111.2.802.1.1.4.1.2.5.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredPorts": "1.3.111.2.802.1.1.4.1.2.5.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredStaticPorts": "1.3.111.2.802.1.1.4.1.2.5.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredForbiddenPorts": "1.3.111.2.802.1.1.4.1.2.5.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStatic": "1.3.111.2.802.1.1.4.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastTable": "1.3.111.2.802.1.1.4.1.3.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastEntry": "1.3.111.2.802.1.1.4.1.3.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastComponentId": "1.3.111.2.802.1.1.4.1.3.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastVlanIndex": "1.3.111.2.802.1.1.4.1.3.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastAddress": "1.3.111.2.802.1.1.4.1.3.1.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastReceivePort": "1.3.111.2.802.1.1.4.1.3.1.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastStaticEgressPorts": "1.3.111.2.802.1.1.4.1.3.1.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastForbiddenEgressPorts": "1.3.111.2.802.1.1.4.1.3.1.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastStorageType": "1.3.111.2.802.1.1.4.1.3.1.1.7",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastRowStatus": "1.3.111.2.802.1.1.4.1.3.1.1.8",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastTable": "1.3.111.2.802.1.1.4.1.3.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastEntry": "1.3.111.2.802.1.1.4.1.3.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastAddress": "1.3.111.2.802.1.1.4.1.3.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastReceivePort": "1.3.111.2.802.1.1.4.1.3.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastStaticEgressPorts": "1.3.111.2.802.1.1.4.1.3.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastForbiddenEgressPorts": "1.3.111.2.802.1.1.4.1.3.2.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastStorageType": "1.3.111.2.802.1.1.4.1.3.2.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastRowStatus": "1.3.111.2.802.1.1.4.1.3.2.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlan": "1.3.111.2.802.1.1.4.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanNumDeletes": "1.3.111.2.802.1.1.4.1.4.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentTable": "1.3.111.2.802.1.1.4.1.4.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentEntry": "1.3.111.2.802.1.1.4.1.4.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanTimeMark": "1.3.111.2.802.1.1.4.1.4.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentComponentId": "1.3.111.2.802.1.1.4.1.4.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanIndex": "1.3.111.2.802.1.1.4.1.4.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanFdbId": "1.3.111.2.802.1.1.4.1.4.2.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentEgressPorts": "1.3.111.2.802.1.1.4.1.4.2.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentUntaggedPorts": "1.3.111.2.802.1.1.4.1.4.2.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStatus": "1.3.111.2.802.1.1.4.1.4.2.1.7",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCreationTime": "1.3.111.2.802.1.1.4.1.4.2.1.8",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticTable": "1.3.111.2.802.1.1.4.1.4.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticEntry": "1.3.111.2.802.1.1.4.1.4.3.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticComponentId": "1.3.111.2.802.1.1.4.1.4.3.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticVlanIndex": "1.3.111.2.802.1.1.4.1.4.3.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticName": "1.3.111.2.802.1.1.4.1.4.3.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticEgressPorts": "1.3.111.2.802.1.1.4.1.4.3.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanForbiddenEgressPorts": "1.3.111.2.802.1.1.4.1.4.3.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticUntaggedPorts": "1.3.111.2.802.1.1.4.1.4.3.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticRowStatus": "1.3.111.2.802.1.1.4.1.4.3.1.7",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNextFreeLocalVlanTable": "1.3.111.2.802.1.1.4.1.4.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNextFreeLocalVlanEntry": "1.3.111.2.802.1.1.4.1.4.4.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNextFreeLocalVlanComponentId": "1.3.111.2.802.1.1.4.1.4.4.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNextFreeLocalVlanIndex": "1.3.111.2.802.1.1.4.1.4.4.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortVlanTable": "1.3.111.2.802.1.1.4.1.4.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortVlanEntry": "1.3.111.2.802.1.1.4.1.4.5.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePvid": "1.3.111.2.802.1.1.4.1.4.5.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortAcceptableFrameTypes": "1.3.111.2.802.1.1.4.1.4.5.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortIngressFiltering": "1.3.111.2.802.1.1.4.1.4.5.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortMvrpEnabledStatus": "1.3.111.2.802.1.1.4.1.4.5.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortMvrpFailedRegistrations": "1.3.111.2.802.1.1.4.1.4.5.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortMvrpLastPduOrigin": "1.3.111.2.802.1.1.4.1.4.5.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortRestrictedVlanRegistration": "1.3.111.2.802.1.1.4.1.4.5.1.7",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortVlanStatisticsTable": "1.3.111.2.802.1.1.4.1.4.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortVlanStatisticsEntry": "1.3.111.2.802.1.1.4.1.4.6.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpVlanPortInFrames": "1.3.111.2.802.1.1.4.1.4.6.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpVlanPortOutFrames": "1.3.111.2.802.1.1.4.1.4.6.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpVlanPortInDiscards": "1.3.111.2.802.1.1.4.1.4.6.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsTable": "1.3.111.2.802.1.1.4.1.4.8",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsEntry": "1.3.111.2.802.1.1.4.1.4.8.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsComponentId": "1.3.111.2.802.1.1.4.1.4.8.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsVlan": "1.3.111.2.802.1.1.4.1.4.8.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsSet": "1.3.111.2.802.1.1.4.1.4.8.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsType": "1.3.111.2.802.1.1.4.1.4.8.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsStatus": "1.3.111.2.802.1.1.4.1.4.8.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsTable": "1.3.111.2.802.1.1.4.1.4.9",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsEntry": "1.3.111.2.802.1.1.4.1.4.9.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsComponentId": "1.3.111.2.802.1.1.4.1.4.9.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsSet": "1.3.111.2.802.1.1.4.1.4.9.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsType": "1.3.111.2.802.1.1.4.1.4.9.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocol": "1.3.111.2.802.1.1.4.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupTable": "1.3.111.2.802.1.1.4.1.5.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupEntry": "1.3.111.2.802.1.1.4.1.5.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupComponentId": "1.3.111.2.802.1.1.4.1.5.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolTemplateFrameType": "1.3.111.2.802.1.1.4.1.5.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolTemplateProtocolValue": "1.3.111.2.802.1.1.4.1.5.1.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupId": "1.3.111.2.802.1.1.4.1.5.1.1.4",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupRowStatus": "1.3.111.2.802.1.1.4.1.5.1.1.5",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolPortTable": "1.3.111.2.802.1.1.4.1.5.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolPortEntry": "1.3.111.2.802.1.1.4.1.5.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolPortGroupId": "1.3.111.2.802.1.1.4.1.5.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolPortGroupVid": "1.3.111.2.802.1.1.4.1.5.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolPortRowStatus": "1.3.111.2.802.1.1.4.1.5.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDX": "1.3.111.2.802.1.1.4.1.6",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDXTable": "1.3.111.2.802.1.1.4.1.6.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDXEntry": "1.3.111.2.802.1.1.4.1.6.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDXLocalVid": "1.3.111.2.802.1.1.4.1.6.1.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDXRelayVid": "1.3.111.2.802.1.1.4.1.6.1.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVIDXRowStatus": "1.3.111.2.802.1.1.4.1.6.1.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEgressVidXTable": "1.3.111.2.802.1.1.4.1.6.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEgressVidXEntry": "1.3.111.2.802.1.1.4.1.6.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEgressVidXRelayVid": "1.3.111.2.802.1.1.4.1.6.2.1.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEgressVidXLocalVid": "1.3.111.2.802.1.1.4.1.6.2.1.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeEgressVidXRowStatus": "1.3.111.2.802.1.1.4.1.6.2.1.3",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeConformance": "1.3.111.2.802.1.1.4.2",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeGroups": "1.3.111.2.802.1.1.4.2.1",
    "IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCompliances": "1.3.111.2.802.1.1.4.2.2",
}

DISPLAY_HINTS = {
    "1.3.111.2.802.1.1.4.1.1.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeComponentId
    "1.3.111.2.802.1.1.4.1.1.2.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortComponentId
    "1.3.111.2.802.1.1.4.1.1.2.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeCVlanPortNumber
    "1.3.111.2.802.1.1.4.1.2.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeFdbComponentId
    "1.3.111.2.802.1.1.4.1.2.2.1.1": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbAddress
    "1.3.111.2.802.1.1.4.1.2.2.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpFdbPort
    "1.3.111.2.802.1.1.4.1.2.3.1.1": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeTpGroupAddress
    "1.3.111.2.802.1.1.4.1.2.4.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardAllVlanIndex
    "1.3.111.2.802.1.1.4.1.2.5.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeForwardUnregisteredVlanIndex
    "1.3.111.2.802.1.1.4.1.3.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastComponentId
    "1.3.111.2.802.1.1.4.1.3.1.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastVlanIndex
    "1.3.111.2.802.1.1.4.1.3.1.1.3": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastAddress
    "1.3.111.2.802.1.1.4.1.3.1.1.4": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticUnicastReceivePort
    "1.3.111.2.802.1.1.4.1.3.2.1.1": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastAddress
    "1.3.111.2.802.1.1.4.1.3.2.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeStaticMulticastReceivePort
    "1.3.111.2.802.1.1.4.1.4.2.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanCurrentComponentId
    "1.3.111.2.802.1.1.4.1.4.2.1.3": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanIndex
    "1.3.111.2.802.1.1.4.1.4.3.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticComponentId
    "1.3.111.2.802.1.1.4.1.4.3.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeVlanStaticVlanIndex
    "1.3.111.2.802.1.1.4.1.4.4.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeNextFreeLocalVlanComponentId
    "1.3.111.2.802.1.1.4.1.4.5.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePvid
    "1.3.111.2.802.1.1.4.1.4.5.1.6": (
        "OctetString",
        "1x:",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgePortMvrpLastPduOrigin
    "1.3.111.2.802.1.1.4.1.4.8.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsComponentId
    "1.3.111.2.802.1.1.4.1.4.8.1.2": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintsVlan
    "1.3.111.2.802.1.1.4.1.4.9.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeLearningConstraintDefaultsComponentId
    "1.3.111.2.802.1.1.4.1.5.1.1.1": (
        "Unsigned32",
        "d",
    ),  # IEEE8021-Q-BRIDGE-MIB::ieee8021QBridgeProtocolGroupComponentId
}
