# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IEEE8023-LAG-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc mib make_cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "IEEE8023-LAG-MIB"
# Metadata
LAST_UPDATED = "2000-06-27"
COMPILED = "2018-06-16"
# MIB Data: name -> oid
MIB = {
    "IEEE8023-LAG-MIB::lagMIB": "1.2.840.10006.300.43",
    "IEEE8023-LAG-MIB::lagMIBObjects": "1.2.840.10006.300.43.1",
    "IEEE8023-LAG-MIB::dot3adAgg": "1.2.840.10006.300.43.1.1",
    "IEEE8023-LAG-MIB::dot3adAggTable": "1.2.840.10006.300.43.1.1.1",
    "IEEE8023-LAG-MIB::dot3adAggEntry": "1.2.840.10006.300.43.1.1.1.1",
    "IEEE8023-LAG-MIB::dot3adAggIndex": "1.2.840.10006.300.43.1.1.1.1.1",
    "IEEE8023-LAG-MIB::dot3adAggMACAddress": "1.2.840.10006.300.43.1.1.1.1.2",
    "IEEE8023-LAG-MIB::dot3adAggActorSystemPriority": "1.2.840.10006.300.43.1.1.1.1.3",
    "IEEE8023-LAG-MIB::dot3adAggActorSystemID": "1.2.840.10006.300.43.1.1.1.1.4",
    "IEEE8023-LAG-MIB::dot3adAggAggregateOrIndividual": "1.2.840.10006.300.43.1.1.1.1.5",
    "IEEE8023-LAG-MIB::dot3adAggActorAdminKey": "1.2.840.10006.300.43.1.1.1.1.6",
    "IEEE8023-LAG-MIB::dot3adAggActorOperKey": "1.2.840.10006.300.43.1.1.1.1.7",
    "IEEE8023-LAG-MIB::dot3adAggPartnerSystemID": "1.2.840.10006.300.43.1.1.1.1.8",
    "IEEE8023-LAG-MIB::dot3adAggPartnerSystemPriority": "1.2.840.10006.300.43.1.1.1.1.9",
    "IEEE8023-LAG-MIB::dot3adAggPartnerOperKey": "1.2.840.10006.300.43.1.1.1.1.10",
    "IEEE8023-LAG-MIB::dot3adAggCollectorMaxDelay": "1.2.840.10006.300.43.1.1.1.1.11",
    "IEEE8023-LAG-MIB::dot3adAggPortListTable": "1.2.840.10006.300.43.1.1.2",
    "IEEE8023-LAG-MIB::dot3adAggPortListEntry": "1.2.840.10006.300.43.1.1.2.1",
    "IEEE8023-LAG-MIB::dot3adAggPortListPorts": "1.2.840.10006.300.43.1.1.2.1.1",
    "IEEE8023-LAG-MIB::dot3adAggPort": "1.2.840.10006.300.43.1.2",
    "IEEE8023-LAG-MIB::dot3adAggPortTable": "1.2.840.10006.300.43.1.2.1",
    "IEEE8023-LAG-MIB::dot3adAggPortEntry": "1.2.840.10006.300.43.1.2.1.1",
    "IEEE8023-LAG-MIB::dot3adAggPortIndex": "1.2.840.10006.300.43.1.2.1.1.1",
    "IEEE8023-LAG-MIB::dot3adAggPortActorSystemPriority": "1.2.840.10006.300.43.1.2.1.1.2",
    "IEEE8023-LAG-MIB::dot3adAggPortActorSystemID": "1.2.840.10006.300.43.1.2.1.1.3",
    "IEEE8023-LAG-MIB::dot3adAggPortActorAdminKey": "1.2.840.10006.300.43.1.2.1.1.4",
    "IEEE8023-LAG-MIB::dot3adAggPortActorOperKey": "1.2.840.10006.300.43.1.2.1.1.5",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminSystemPriority": "1.2.840.10006.300.43.1.2.1.1.6",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperSystemPriority": "1.2.840.10006.300.43.1.2.1.1.7",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminSystemID": "1.2.840.10006.300.43.1.2.1.1.8",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperSystemID": "1.2.840.10006.300.43.1.2.1.1.9",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminKey": "1.2.840.10006.300.43.1.2.1.1.10",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperKey": "1.2.840.10006.300.43.1.2.1.1.11",
    "IEEE8023-LAG-MIB::dot3adAggPortSelectedAggID": "1.2.840.10006.300.43.1.2.1.1.12",
    "IEEE8023-LAG-MIB::dot3adAggPortAttachedAggID": "1.2.840.10006.300.43.1.2.1.1.13",
    "IEEE8023-LAG-MIB::dot3adAggPortActorPort": "1.2.840.10006.300.43.1.2.1.1.14",
    "IEEE8023-LAG-MIB::dot3adAggPortActorPortPriority": "1.2.840.10006.300.43.1.2.1.1.15",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminPort": "1.2.840.10006.300.43.1.2.1.1.16",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperPort": "1.2.840.10006.300.43.1.2.1.1.17",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminPortPriority": "1.2.840.10006.300.43.1.2.1.1.18",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperPortPriority": "1.2.840.10006.300.43.1.2.1.1.19",
    "IEEE8023-LAG-MIB::dot3adAggPortActorAdminState": "1.2.840.10006.300.43.1.2.1.1.20",
    "IEEE8023-LAG-MIB::dot3adAggPortActorOperState": "1.2.840.10006.300.43.1.2.1.1.21",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminState": "1.2.840.10006.300.43.1.2.1.1.22",
    "IEEE8023-LAG-MIB::dot3adAggPortPartnerOperState": "1.2.840.10006.300.43.1.2.1.1.23",
    "IEEE8023-LAG-MIB::dot3adAggPortAggregateOrIndividual": "1.2.840.10006.300.43.1.2.1.1.24",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsTable": "1.2.840.10006.300.43.1.2.2",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsEntry": "1.2.840.10006.300.43.1.2.2.1",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsLACPDUsRx": "1.2.840.10006.300.43.1.2.2.1.1",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsMarkerPDUsRx": "1.2.840.10006.300.43.1.2.2.1.2",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsMarkerResponsePDUsRx": "1.2.840.10006.300.43.1.2.2.1.3",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsUnknownRx": "1.2.840.10006.300.43.1.2.2.1.4",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsIllegalRx": "1.2.840.10006.300.43.1.2.2.1.5",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsLACPDUsTx": "1.2.840.10006.300.43.1.2.2.1.6",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsMarkerPDUsTx": "1.2.840.10006.300.43.1.2.2.1.7",
    "IEEE8023-LAG-MIB::dot3adAggPortStatsMarkerResponsePDUsTx": "1.2.840.10006.300.43.1.2.2.1.8",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugTable": "1.2.840.10006.300.43.1.2.3",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugEntry": "1.2.840.10006.300.43.1.2.3.1",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugRxState": "1.2.840.10006.300.43.1.2.3.1.1",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugLastRxTime": "1.2.840.10006.300.43.1.2.3.1.2",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugMuxState": "1.2.840.10006.300.43.1.2.3.1.3",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugMuxReason": "1.2.840.10006.300.43.1.2.3.1.4",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugActorChurnState": "1.2.840.10006.300.43.1.2.3.1.5",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugPartnerChurnState": "1.2.840.10006.300.43.1.2.3.1.6",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugActorChurnCount": "1.2.840.10006.300.43.1.2.3.1.7",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugPartnerChurnCount": "1.2.840.10006.300.43.1.2.3.1.8",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugActorSyncTransitionCount": "1.2.840.10006.300.43.1.2.3.1.9",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugPartnerSyncTransitionCount": "1.2.840.10006.300.43.1.2.3.1.10",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugActorChangeCount": "1.2.840.10006.300.43.1.2.3.1.11",
    "IEEE8023-LAG-MIB::dot3adAggPortDebugPartnerChangeCount": "1.2.840.10006.300.43.1.2.3.1.12",
    "IEEE8023-LAG-MIB::dot3adTablesLastChanged": "1.2.840.10006.300.43.1.3",
    "IEEE8023-LAG-MIB::dot3adAggConformance": "1.2.840.10006.300.43.2",
    "IEEE8023-LAG-MIB::dot3adAggGroups": "1.2.840.10006.300.43.2.1",
    "IEEE8023-LAG-MIB::dot3adAggCompliances": "1.2.840.10006.300.43.2.2"
}
