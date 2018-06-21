# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CISCO-VRF-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "CISCO-VRF-MIB"
# Metadata
LAST_UPDATED = "2009-12-10"
COMPILED = "2018-06-09"
# MIB Data: name -> oid
MIB = {
    "CISCO-VRF-MIB::ciscoVrfMIB": "1.3.6.1.4.1.9.9.711",
    "CISCO-VRF-MIB::ciscoVrfMIBNotifs": "1.3.6.1.4.1.9.9.711.0",
    "CISCO-VRF-MIB::cvVrfIfUp": "1.3.6.1.4.1.9.9.711.0.1",
    "CISCO-VRF-MIB::cvVrfIfDown": "1.3.6.1.4.1.9.9.711.0.2",
    "CISCO-VRF-MIB::cvVnetTrunkUp": "1.3.6.1.4.1.9.9.711.0.3",
    "CISCO-VRF-MIB::cvVnetTrunkDown": "1.3.6.1.4.1.9.9.711.0.4",
    "CISCO-VRF-MIB::ciscoVrfMIBObjects": "1.3.6.1.4.1.9.9.711.1",
    "CISCO-VRF-MIB::cvVrf": "1.3.6.1.4.1.9.9.711.1.1",
    "CISCO-VRF-MIB::cvVrfTable": "1.3.6.1.4.1.9.9.711.1.1.1",
    "CISCO-VRF-MIB::cvVrfEntry": "1.3.6.1.4.1.9.9.711.1.1.1.1",
    "CISCO-VRF-MIB::cvVrfIndex": "1.3.6.1.4.1.9.9.711.1.1.1.1.1",
    "CISCO-VRF-MIB::cvVrfName": "1.3.6.1.4.1.9.9.711.1.1.1.1.2",
    "CISCO-VRF-MIB::cvVrfVnetTag": "1.3.6.1.4.1.9.9.711.1.1.1.1.3",
    "CISCO-VRF-MIB::cvVrfOperStatus": "1.3.6.1.4.1.9.9.711.1.1.1.1.4",
    "CISCO-VRF-MIB::cvVrfRouteDistProt": "1.3.6.1.4.1.9.9.711.1.1.1.1.5",
    "CISCO-VRF-MIB::cvVrfStorageType": "1.3.6.1.4.1.9.9.711.1.1.1.1.6",
    "CISCO-VRF-MIB::cvVrfRowStatus": "1.3.6.1.4.1.9.9.711.1.1.1.1.7",
    "CISCO-VRF-MIB::cvVrfListTable": "1.3.6.1.4.1.9.9.711.1.1.2",
    "CISCO-VRF-MIB::cvVrfListEntry": "1.3.6.1.4.1.9.9.711.1.1.2.1",
    "CISCO-VRF-MIB::cvVrfListName": "1.3.6.1.4.1.9.9.711.1.1.2.1.1",
    "CISCO-VRF-MIB::cvVrfListVindex": "1.3.6.1.4.1.9.9.711.1.1.2.1.2",
    "CISCO-VRF-MIB::cvVrfListVrfIndex": "1.3.6.1.4.1.9.9.711.1.1.2.1.3",
    "CISCO-VRF-MIB::cvVrfListStorageType": "1.3.6.1.4.1.9.9.711.1.1.2.1.4",
    "CISCO-VRF-MIB::cvVrfListRowStatus": "1.3.6.1.4.1.9.9.711.1.1.2.1.5",
    "CISCO-VRF-MIB::cvInterface": "1.3.6.1.4.1.9.9.711.1.2",
    "CISCO-VRF-MIB::cvVrfInterfaceTable": "1.3.6.1.4.1.9.9.711.1.2.1",
    "CISCO-VRF-MIB::cvVrfInterfaceEntry": "1.3.6.1.4.1.9.9.711.1.2.1.1",
    "CISCO-VRF-MIB::cvVrfInterfaceIndex": "1.3.6.1.4.1.9.9.711.1.2.1.1.1",
    "CISCO-VRF-MIB::cvVrfInterfaceType": "1.3.6.1.4.1.9.9.711.1.2.1.1.2",
    "CISCO-VRF-MIB::cvVrfInterfaceVnetTagOverride": "1.3.6.1.4.1.9.9.711.1.2.1.1.3",
    "CISCO-VRF-MIB::cvVrfInterfaceStorageType": "1.3.6.1.4.1.9.9.711.1.2.1.1.4",
    "CISCO-VRF-MIB::cvVrfInterfaceRowStatus": "1.3.6.1.4.1.9.9.711.1.2.1.1.5",
    "CISCO-VRF-MIB::cvInterfaceTable": "1.3.6.1.4.1.9.9.711.1.2.2",
    "CISCO-VRF-MIB::cvInterfaceEntry": "1.3.6.1.4.1.9.9.711.1.2.2.1",
    "CISCO-VRF-MIB::cvInterfaceVnetTrunkEnabled": "1.3.6.1.4.1.9.9.711.1.2.2.1.1",
    "CISCO-VRF-MIB::cvInterfaceVnetVrfList": "1.3.6.1.4.1.9.9.711.1.2.2.1.2",
    "CISCO-VRF-MIB::cvNotifCntl": "1.3.6.1.4.1.9.9.711.1.3",
    "CISCO-VRF-MIB::cvVrfIfNotifEnable": "1.3.6.1.4.1.9.9.711.1.3.1",
    "CISCO-VRF-MIB::cvVnetTrunkNotifEnable": "1.3.6.1.4.1.9.9.711.1.3.2",
    "CISCO-VRF-MIB::ciscoVrfMIBConform": "1.3.6.1.4.1.9.9.711.2",
    "CISCO-VRF-MIB::cvMIBGroups": "1.3.6.1.4.1.9.9.711.2.1",
    "CISCO-VRF-MIB::cvMIBCompliances": "1.3.6.1.4.1.9.9.711.2.2"
}
