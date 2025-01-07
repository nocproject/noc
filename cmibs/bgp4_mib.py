# ----------------------------------------------------------------------
# BGP4-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "BGP4-MIB"

# Metadata
LAST_UPDATED = "2006-01-11"
COMPILED = "2025-01-06"

# MIB Data: name -> oid
MIB = {
    "BGP4-MIB::bgp": "1.3.6.1.2.1.15",
    "BGP4-MIB::bgpNotification": "1.3.6.1.2.1.15.0",
    "BGP4-MIB::bgpEstablishedNotification": "1.3.6.1.2.1.15.0.1",
    "BGP4-MIB::bgpBackwardTransNotification": "1.3.6.1.2.1.15.0.2",
    "BGP4-MIB::bgpVersion": "1.3.6.1.2.1.15.1",
    "BGP4-MIB::bgpLocalAs": "1.3.6.1.2.1.15.2",
    "BGP4-MIB::bgpPeerTable": "1.3.6.1.2.1.15.3",
    "BGP4-MIB::bgpPeerEntry": "1.3.6.1.2.1.15.3.1",
    "BGP4-MIB::bgpPeerIdentifier": "1.3.6.1.2.1.15.3.1.1",
    "BGP4-MIB::bgpPeerState": "1.3.6.1.2.1.15.3.1.2",
    "BGP4-MIB::bgpPeerAdminStatus": "1.3.6.1.2.1.15.3.1.3",
    "BGP4-MIB::bgpPeerNegotiatedVersion": "1.3.6.1.2.1.15.3.1.4",
    "BGP4-MIB::bgpPeerLocalAddr": "1.3.6.1.2.1.15.3.1.5",
    "BGP4-MIB::bgpPeerLocalPort": "1.3.6.1.2.1.15.3.1.6",
    "BGP4-MIB::bgpPeerRemoteAddr": "1.3.6.1.2.1.15.3.1.7",
    "BGP4-MIB::bgpPeerRemotePort": "1.3.6.1.2.1.15.3.1.8",
    "BGP4-MIB::bgpPeerRemoteAs": "1.3.6.1.2.1.15.3.1.9",
    "BGP4-MIB::bgpPeerInUpdates": "1.3.6.1.2.1.15.3.1.10",
    "BGP4-MIB::bgpPeerOutUpdates": "1.3.6.1.2.1.15.3.1.11",
    "BGP4-MIB::bgpPeerInTotalMessages": "1.3.6.1.2.1.15.3.1.12",
    "BGP4-MIB::bgpPeerOutTotalMessages": "1.3.6.1.2.1.15.3.1.13",
    "BGP4-MIB::bgpPeerLastError": "1.3.6.1.2.1.15.3.1.14",
    "BGP4-MIB::bgpPeerFsmEstablishedTransitions": "1.3.6.1.2.1.15.3.1.15",
    "BGP4-MIB::bgpPeerFsmEstablishedTime": "1.3.6.1.2.1.15.3.1.16",
    "BGP4-MIB::bgpPeerConnectRetryInterval": "1.3.6.1.2.1.15.3.1.17",
    "BGP4-MIB::bgpPeerHoldTime": "1.3.6.1.2.1.15.3.1.18",
    "BGP4-MIB::bgpPeerKeepAlive": "1.3.6.1.2.1.15.3.1.19",
    "BGP4-MIB::bgpPeerHoldTimeConfigured": "1.3.6.1.2.1.15.3.1.20",
    "BGP4-MIB::bgpPeerKeepAliveConfigured": "1.3.6.1.2.1.15.3.1.21",
    "BGP4-MIB::bgpPeerMinASOriginationInterval": "1.3.6.1.2.1.15.3.1.22",
    "BGP4-MIB::bgpPeerMinRouteAdvertisementInterval": "1.3.6.1.2.1.15.3.1.23",
    "BGP4-MIB::bgpPeerInUpdateElapsedTime": "1.3.6.1.2.1.15.3.1.24",
    "BGP4-MIB::bgpIdentifier": "1.3.6.1.2.1.15.4",
    "BGP4-MIB::bgpRcvdPathAttrTable": "1.3.6.1.2.1.15.5",
    "BGP4-MIB::bgpPathAttrEntry": "1.3.6.1.2.1.15.5.1",
    "BGP4-MIB::bgpPathAttrPeer": "1.3.6.1.2.1.15.5.1.1",
    "BGP4-MIB::bgpPathAttrDestNetwork": "1.3.6.1.2.1.15.5.1.2",
    "BGP4-MIB::bgpPathAttrOrigin": "1.3.6.1.2.1.15.5.1.3",
    "BGP4-MIB::bgpPathAttrASPath": "1.3.6.1.2.1.15.5.1.4",
    "BGP4-MIB::bgpPathAttrNextHop": "1.3.6.1.2.1.15.5.1.5",
    "BGP4-MIB::bgpPathAttrInterASMetric": "1.3.6.1.2.1.15.5.1.6",
    "BGP4-MIB::bgp4PathAttrTable": "1.3.6.1.2.1.15.6",
    "BGP4-MIB::bgp4PathAttrEntry": "1.3.6.1.2.1.15.6.1",
    "BGP4-MIB::bgp4PathAttrPeer": "1.3.6.1.2.1.15.6.1.1",
    "BGP4-MIB::bgp4PathAttrIpAddrPrefixLen": "1.3.6.1.2.1.15.6.1.2",
    "BGP4-MIB::bgp4PathAttrIpAddrPrefix": "1.3.6.1.2.1.15.6.1.3",
    "BGP4-MIB::bgp4PathAttrOrigin": "1.3.6.1.2.1.15.6.1.4",
    "BGP4-MIB::bgp4PathAttrASPathSegment": "1.3.6.1.2.1.15.6.1.5",
    "BGP4-MIB::bgp4PathAttrNextHop": "1.3.6.1.2.1.15.6.1.6",
    "BGP4-MIB::bgp4PathAttrMultiExitDisc": "1.3.6.1.2.1.15.6.1.7",
    "BGP4-MIB::bgp4PathAttrLocalPref": "1.3.6.1.2.1.15.6.1.8",
    "BGP4-MIB::bgp4PathAttrAtomicAggregate": "1.3.6.1.2.1.15.6.1.9",
    "BGP4-MIB::bgp4PathAttrAggregatorAS": "1.3.6.1.2.1.15.6.1.10",
    "BGP4-MIB::bgp4PathAttrAggregatorAddr": "1.3.6.1.2.1.15.6.1.11",
    "BGP4-MIB::bgp4PathAttrCalcLocalPref": "1.3.6.1.2.1.15.6.1.12",
    "BGP4-MIB::bgp4PathAttrBest": "1.3.6.1.2.1.15.6.1.13",
    "BGP4-MIB::bgp4PathAttrUnknown": "1.3.6.1.2.1.15.6.1.14",
    "BGP4-MIB::bgpTraps": "1.3.6.1.2.1.15.7",
    "BGP4-MIB::bgpEstablished": "1.3.6.1.2.1.15.7.1",
    "BGP4-MIB::bgpBackwardTransition": "1.3.6.1.2.1.15.7.2",
    "BGP4-MIB::bgp4MIBConformance": "1.3.6.1.2.1.15.8",
    "BGP4-MIB::bgp4MIBCompliances": "1.3.6.1.2.1.15.8.1",
    "BGP4-MIB::bgp4MIBGroups": "1.3.6.1.2.1.15.8.2",
}

DISPLAY_HINTS = {}
