# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CISCO-CDP-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "CISCO-CDP-MIB"
# Metadata
LAST_UPDATED = "2005-03-21"
COMPILED = "2018-06-09"
# MIB Data: name -> oid
MIB = {
    "CISCO-CDP-MIB::ciscoCdpMIB": "1.3.6.1.4.1.9.9.23",
    "CISCO-CDP-MIB::ciscoCdpMIBObjects": "1.3.6.1.4.1.9.9.23.1",
    "CISCO-CDP-MIB::cdpInterface": "1.3.6.1.4.1.9.9.23.1.1",
    "CISCO-CDP-MIB::cdpInterfaceTable": "1.3.6.1.4.1.9.9.23.1.1.1",
    "CISCO-CDP-MIB::cdpInterfaceEntry": "1.3.6.1.4.1.9.9.23.1.1.1.1",
    "CISCO-CDP-MIB::cdpInterfaceIfIndex": "1.3.6.1.4.1.9.9.23.1.1.1.1.1",
    "CISCO-CDP-MIB::cdpInterfaceEnable": "1.3.6.1.4.1.9.9.23.1.1.1.1.2",
    "CISCO-CDP-MIB::cdpInterfaceMessageInterval": "1.3.6.1.4.1.9.9.23.1.1.1.1.3",
    "CISCO-CDP-MIB::cdpInterfaceGroup": "1.3.6.1.4.1.9.9.23.1.1.1.1.4",
    "CISCO-CDP-MIB::cdpInterfacePort": "1.3.6.1.4.1.9.9.23.1.1.1.1.5",
    "CISCO-CDP-MIB::cdpInterfaceName": "1.3.6.1.4.1.9.9.23.1.1.1.1.6",
    "CISCO-CDP-MIB::cdpInterfaceExtTable": "1.3.6.1.4.1.9.9.23.1.1.2",
    "CISCO-CDP-MIB::cdpInterfaceExtEntry": "1.3.6.1.4.1.9.9.23.1.1.2.1",
    "CISCO-CDP-MIB::cdpInterfaceExtendedTrust": "1.3.6.1.4.1.9.9.23.1.1.2.1.1",
    "CISCO-CDP-MIB::cdpInterfaceCosForUntrustedPort": "1.3.6.1.4.1.9.9.23.1.1.2.1.2",
    "CISCO-CDP-MIB::cdpCache": "1.3.6.1.4.1.9.9.23.1.2",
    "CISCO-CDP-MIB::cdpCacheTable": "1.3.6.1.4.1.9.9.23.1.2.1",
    "CISCO-CDP-MIB::cdpCacheEntry": "1.3.6.1.4.1.9.9.23.1.2.1.1",
    "CISCO-CDP-MIB::cdpCacheIfIndex": "1.3.6.1.4.1.9.9.23.1.2.1.1.1",
    "CISCO-CDP-MIB::cdpCacheDeviceIndex": "1.3.6.1.4.1.9.9.23.1.2.1.1.2",
    "CISCO-CDP-MIB::cdpCacheAddressType": "1.3.6.1.4.1.9.9.23.1.2.1.1.3",
    "CISCO-CDP-MIB::cdpCacheAddress": "1.3.6.1.4.1.9.9.23.1.2.1.1.4",
    "CISCO-CDP-MIB::cdpCacheVersion": "1.3.6.1.4.1.9.9.23.1.2.1.1.5",
    "CISCO-CDP-MIB::cdpCacheDeviceId": "1.3.6.1.4.1.9.9.23.1.2.1.1.6",
    "CISCO-CDP-MIB::cdpCacheDevicePort": "1.3.6.1.4.1.9.9.23.1.2.1.1.7",
    "CISCO-CDP-MIB::cdpCachePlatform": "1.3.6.1.4.1.9.9.23.1.2.1.1.8",
    "CISCO-CDP-MIB::cdpCacheCapabilities": "1.3.6.1.4.1.9.9.23.1.2.1.1.9",
    "CISCO-CDP-MIB::cdpCacheVTPMgmtDomain": "1.3.6.1.4.1.9.9.23.1.2.1.1.10",
    "CISCO-CDP-MIB::cdpCacheNativeVLAN": "1.3.6.1.4.1.9.9.23.1.2.1.1.11",
    "CISCO-CDP-MIB::cdpCacheDuplex": "1.3.6.1.4.1.9.9.23.1.2.1.1.12",
    "CISCO-CDP-MIB::cdpCacheApplianceID": "1.3.6.1.4.1.9.9.23.1.2.1.1.13",
    "CISCO-CDP-MIB::cdpCacheVlanID": "1.3.6.1.4.1.9.9.23.1.2.1.1.14",
    "CISCO-CDP-MIB::cdpCachePowerConsumption": "1.3.6.1.4.1.9.9.23.1.2.1.1.15",
    "CISCO-CDP-MIB::cdpCacheMTU": "1.3.6.1.4.1.9.9.23.1.2.1.1.16",
    "CISCO-CDP-MIB::cdpCacheSysName": "1.3.6.1.4.1.9.9.23.1.2.1.1.17",
    "CISCO-CDP-MIB::cdpCacheSysObjectID": "1.3.6.1.4.1.9.9.23.1.2.1.1.18",
    "CISCO-CDP-MIB::cdpCachePrimaryMgmtAddrType": "1.3.6.1.4.1.9.9.23.1.2.1.1.19",
    "CISCO-CDP-MIB::cdpCachePrimaryMgmtAddr": "1.3.6.1.4.1.9.9.23.1.2.1.1.20",
    "CISCO-CDP-MIB::cdpCacheSecondaryMgmtAddrType": "1.3.6.1.4.1.9.9.23.1.2.1.1.21",
    "CISCO-CDP-MIB::cdpCacheSecondaryMgmtAddr": "1.3.6.1.4.1.9.9.23.1.2.1.1.22",
    "CISCO-CDP-MIB::cdpCachePhysLocation": "1.3.6.1.4.1.9.9.23.1.2.1.1.23",
    "CISCO-CDP-MIB::cdpCacheLastChange": "1.3.6.1.4.1.9.9.23.1.2.1.1.24",
    "CISCO-CDP-MIB::cdpCtAddressTable": "1.3.6.1.4.1.9.9.23.1.2.2",
    "CISCO-CDP-MIB::cdpCtAddressEntry": "1.3.6.1.4.1.9.9.23.1.2.2.1",
    "CISCO-CDP-MIB::cdpCtAddressIndex": "1.3.6.1.4.1.9.9.23.1.2.2.1.3",
    "CISCO-CDP-MIB::cdpCtAddressType": "1.3.6.1.4.1.9.9.23.1.2.2.1.4",
    "CISCO-CDP-MIB::cdpCtAddress": "1.3.6.1.4.1.9.9.23.1.2.2.1.5",
    "CISCO-CDP-MIB::cdpGlobal": "1.3.6.1.4.1.9.9.23.1.3",
    "CISCO-CDP-MIB::cdpGlobalRun": "1.3.6.1.4.1.9.9.23.1.3.1",
    "CISCO-CDP-MIB::cdpGlobalMessageInterval": "1.3.6.1.4.1.9.9.23.1.3.2",
    "CISCO-CDP-MIB::cdpGlobalHoldTime": "1.3.6.1.4.1.9.9.23.1.3.3",
    "CISCO-CDP-MIB::cdpGlobalDeviceId": "1.3.6.1.4.1.9.9.23.1.3.4",
    "CISCO-CDP-MIB::cdpGlobalLastChange": "1.3.6.1.4.1.9.9.23.1.3.5",
    "CISCO-CDP-MIB::cdpGlobalDeviceIdFormatCpb": "1.3.6.1.4.1.9.9.23.1.3.6",
    "CISCO-CDP-MIB::cdpGlobalDeviceIdFormat": "1.3.6.1.4.1.9.9.23.1.3.7",
    "CISCO-CDP-MIB::ciscoCdpMIBConformance": "1.3.6.1.4.1.9.9.23.2",
    "CISCO-CDP-MIB::ciscoCdpMIBCompliances": "1.3.6.1.4.1.9.9.23.2.1",
    "CISCO-CDP-MIB::ciscoCdpMIBGroups": "1.3.6.1.4.1.9.9.23.2.2"
}
