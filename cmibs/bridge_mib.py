# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BRIDGE-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "BRIDGE-MIB"
# Metadata
LAST_UPDATED = "2005-09-19"
COMPILED = "2017-11-04"
# MIB Data: name -> oid
MIB = {
    "BRIDGE-MIB::dot1dBridge": "1.3.6.1.2.1.17",
    "BRIDGE-MIB::dot1dNotifications": "1.3.6.1.2.1.17.0",
    "BRIDGE-MIB::newRoot": "1.3.6.1.2.1.17.0.1",
    "BRIDGE-MIB::topologyChange": "1.3.6.1.2.1.17.0.2",
    "BRIDGE-MIB::dot1dBase": "1.3.6.1.2.1.17.1",
    "BRIDGE-MIB::dot1dBaseBridgeAddress": "1.3.6.1.2.1.17.1.1",
    "BRIDGE-MIB::dot1dBaseNumPorts": "1.3.6.1.2.1.17.1.2",
    "BRIDGE-MIB::dot1dBaseType": "1.3.6.1.2.1.17.1.3",
    "BRIDGE-MIB::dot1dBasePortTable": "1.3.6.1.2.1.17.1.4",
    "BRIDGE-MIB::dot1dBasePortEntry": "1.3.6.1.2.1.17.1.4.1",
    "BRIDGE-MIB::dot1dBasePort": "1.3.6.1.2.1.17.1.4.1.1",
    "BRIDGE-MIB::dot1dBasePortIfIndex": "1.3.6.1.2.1.17.1.4.1.2",
    "BRIDGE-MIB::dot1dBasePortCircuit": "1.3.6.1.2.1.17.1.4.1.3",
    "BRIDGE-MIB::dot1dBasePortDelayExceededDiscards": "1.3.6.1.2.1.17.1.4.1.4",
    "BRIDGE-MIB::dot1dBasePortMtuExceededDiscards": "1.3.6.1.2.1.17.1.4.1.5",
    "BRIDGE-MIB::dot1dStp": "1.3.6.1.2.1.17.2",
    "BRIDGE-MIB::dot1dStpProtocolSpecification": "1.3.6.1.2.1.17.2.1",
    "BRIDGE-MIB::dot1dStpPriority": "1.3.6.1.2.1.17.2.2",
    "BRIDGE-MIB::dot1dStpTimeSinceTopologyChange": "1.3.6.1.2.1.17.2.3",
    "BRIDGE-MIB::dot1dStpTopChanges": "1.3.6.1.2.1.17.2.4",
    "BRIDGE-MIB::dot1dStpDesignatedRoot": "1.3.6.1.2.1.17.2.5",
    "BRIDGE-MIB::dot1dStpRootCost": "1.3.6.1.2.1.17.2.6",
    "BRIDGE-MIB::dot1dStpRootPort": "1.3.6.1.2.1.17.2.7",
    "BRIDGE-MIB::dot1dStpMaxAge": "1.3.6.1.2.1.17.2.8",
    "BRIDGE-MIB::dot1dStpHelloTime": "1.3.6.1.2.1.17.2.9",
    "BRIDGE-MIB::dot1dStpHoldTime": "1.3.6.1.2.1.17.2.10",
    "BRIDGE-MIB::dot1dStpForwardDelay": "1.3.6.1.2.1.17.2.11",
    "BRIDGE-MIB::dot1dStpBridgeMaxAge": "1.3.6.1.2.1.17.2.12",
    "BRIDGE-MIB::dot1dStpBridgeHelloTime": "1.3.6.1.2.1.17.2.13",
    "BRIDGE-MIB::dot1dStpBridgeForwardDelay": "1.3.6.1.2.1.17.2.14",
    "BRIDGE-MIB::dot1dStpPortTable": "1.3.6.1.2.1.17.2.15",
    "BRIDGE-MIB::dot1dStpPortEntry": "1.3.6.1.2.1.17.2.15.1",
    "BRIDGE-MIB::dot1dStpPort": "1.3.6.1.2.1.17.2.15.1.1",
    "BRIDGE-MIB::dot1dStpPortPriority": "1.3.6.1.2.1.17.2.15.1.2",
    "BRIDGE-MIB::dot1dStpPortState": "1.3.6.1.2.1.17.2.15.1.3",
    "BRIDGE-MIB::dot1dStpPortEnable": "1.3.6.1.2.1.17.2.15.1.4",
    "BRIDGE-MIB::dot1dStpPortPathCost": "1.3.6.1.2.1.17.2.15.1.5",
    "BRIDGE-MIB::dot1dStpPortDesignatedRoot": "1.3.6.1.2.1.17.2.15.1.6",
    "BRIDGE-MIB::dot1dStpPortDesignatedCost": "1.3.6.1.2.1.17.2.15.1.7",
    "BRIDGE-MIB::dot1dStpPortDesignatedBridge": "1.3.6.1.2.1.17.2.15.1.8",
    "BRIDGE-MIB::dot1dStpPortDesignatedPort": "1.3.6.1.2.1.17.2.15.1.9",
    "BRIDGE-MIB::dot1dStpPortForwardTransitions": "1.3.6.1.2.1.17.2.15.1.10",
    "BRIDGE-MIB::dot1dStpPortPathCost32": "1.3.6.1.2.1.17.2.15.1.11",
    "BRIDGE-MIB::dot1dSr": "1.3.6.1.2.1.17.3",
    "BRIDGE-MIB::dot1dTp": "1.3.6.1.2.1.17.4",
    "BRIDGE-MIB::dot1dTpLearnedEntryDiscards": "1.3.6.1.2.1.17.4.1",
    "BRIDGE-MIB::dot1dTpAgingTime": "1.3.6.1.2.1.17.4.2",
    "BRIDGE-MIB::dot1dTpFdbTable": "1.3.6.1.2.1.17.4.3",
    "BRIDGE-MIB::dot1dTpFdbEntry": "1.3.6.1.2.1.17.4.3.1",
    "BRIDGE-MIB::dot1dTpFdbAddress": "1.3.6.1.2.1.17.4.3.1.1",
    "BRIDGE-MIB::dot1dTpFdbPort": "1.3.6.1.2.1.17.4.3.1.2",
    "BRIDGE-MIB::dot1dTpFdbStatus": "1.3.6.1.2.1.17.4.3.1.3",
    "BRIDGE-MIB::dot1dTpPortTable": "1.3.6.1.2.1.17.4.4",
    "BRIDGE-MIB::dot1dTpPortEntry": "1.3.6.1.2.1.17.4.4.1",
    "BRIDGE-MIB::dot1dTpPort": "1.3.6.1.2.1.17.4.4.1.1",
    "BRIDGE-MIB::dot1dTpPortMaxInfo": "1.3.6.1.2.1.17.4.4.1.2",
    "BRIDGE-MIB::dot1dTpPortInFrames": "1.3.6.1.2.1.17.4.4.1.3",
    "BRIDGE-MIB::dot1dTpPortOutFrames": "1.3.6.1.2.1.17.4.4.1.4",
    "BRIDGE-MIB::dot1dTpPortInDiscards": "1.3.6.1.2.1.17.4.4.1.5",
    "BRIDGE-MIB::dot1dStatic": "1.3.6.1.2.1.17.5",
    "BRIDGE-MIB::dot1dStaticTable": "1.3.6.1.2.1.17.5.1",
    "BRIDGE-MIB::dot1dStaticEntry": "1.3.6.1.2.1.17.5.1.1",
    "BRIDGE-MIB::dot1dStaticAddress": "1.3.6.1.2.1.17.5.1.1.1",
    "BRIDGE-MIB::dot1dStaticReceivePort": "1.3.6.1.2.1.17.5.1.1.2",
    "BRIDGE-MIB::dot1dStaticAllowedToGoTo": "1.3.6.1.2.1.17.5.1.1.3",
    "BRIDGE-MIB::dot1dStaticStatus": "1.3.6.1.2.1.17.5.1.1.4",
    "BRIDGE-MIB::dot1dConformance": "1.3.6.1.2.1.17.8",
    "BRIDGE-MIB::dot1dGroups": "1.3.6.1.2.1.17.8.1",
    "BRIDGE-MIB::dot1dCompliances": "1.3.6.1.2.1.17.8.2"
}
