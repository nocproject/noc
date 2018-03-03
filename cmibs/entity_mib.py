# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ENTITY-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "ENTITY-MIB"
# Metadata
LAST_UPDATED = "2005-08-10"
COMPILED = "2018-03-03"
# MIB Data: name -> oid
MIB = {
    "ENTITY-MIB::entityMIB": "1.3.6.1.2.1.47",
    "ENTITY-MIB::entityMIBObjects": "1.3.6.1.2.1.47.1",
    "ENTITY-MIB::entityPhysical": "1.3.6.1.2.1.47.1.1",
    "ENTITY-MIB::entPhysicalTable": "1.3.6.1.2.1.47.1.1.1",
    "ENTITY-MIB::entPhysicalEntry": "1.3.6.1.2.1.47.1.1.1.1",
    "ENTITY-MIB::entPhysicalIndex": "1.3.6.1.2.1.47.1.1.1.1.1",
    "ENTITY-MIB::entPhysicalDescr": "1.3.6.1.2.1.47.1.1.1.1.2",
    "ENTITY-MIB::entPhysicalVendorType": "1.3.6.1.2.1.47.1.1.1.1.3",
    "ENTITY-MIB::entPhysicalContainedIn": "1.3.6.1.2.1.47.1.1.1.1.4",
    "ENTITY-MIB::entPhysicalClass": "1.3.6.1.2.1.47.1.1.1.1.5",
    "ENTITY-MIB::entPhysicalParentRelPos": "1.3.6.1.2.1.47.1.1.1.1.6",
    "ENTITY-MIB::entPhysicalName": "1.3.6.1.2.1.47.1.1.1.1.7",
    "ENTITY-MIB::entPhysicalHardwareRev": "1.3.6.1.2.1.47.1.1.1.1.8",
    "ENTITY-MIB::entPhysicalFirmwareRev": "1.3.6.1.2.1.47.1.1.1.1.9",
    "ENTITY-MIB::entPhysicalSoftwareRev": "1.3.6.1.2.1.47.1.1.1.1.10",
    "ENTITY-MIB::entPhysicalSerialNum": "1.3.6.1.2.1.47.1.1.1.1.11",
    "ENTITY-MIB::entPhysicalMfgName": "1.3.6.1.2.1.47.1.1.1.1.12",
    "ENTITY-MIB::entPhysicalModelName": "1.3.6.1.2.1.47.1.1.1.1.13",
    "ENTITY-MIB::entPhysicalAlias": "1.3.6.1.2.1.47.1.1.1.1.14",
    "ENTITY-MIB::entPhysicalAssetID": "1.3.6.1.2.1.47.1.1.1.1.15",
    "ENTITY-MIB::entPhysicalIsFRU": "1.3.6.1.2.1.47.1.1.1.1.16",
    "ENTITY-MIB::entPhysicalMfgDate": "1.3.6.1.2.1.47.1.1.1.1.17",
    "ENTITY-MIB::entPhysicalUris": "1.3.6.1.2.1.47.1.1.1.1.18",
    "ENTITY-MIB::entityLogical": "1.3.6.1.2.1.47.1.2",
    "ENTITY-MIB::entLogicalTable": "1.3.6.1.2.1.47.1.2.1",
    "ENTITY-MIB::entLogicalEntry": "1.3.6.1.2.1.47.1.2.1.1",
    "ENTITY-MIB::entLogicalIndex": "1.3.6.1.2.1.47.1.2.1.1.1",
    "ENTITY-MIB::entLogicalDescr": "1.3.6.1.2.1.47.1.2.1.1.2",
    "ENTITY-MIB::entLogicalType": "1.3.6.1.2.1.47.1.2.1.1.3",
    "ENTITY-MIB::entLogicalCommunity": "1.3.6.1.2.1.47.1.2.1.1.4",
    "ENTITY-MIB::entLogicalTAddress": "1.3.6.1.2.1.47.1.2.1.1.5",
    "ENTITY-MIB::entLogicalTDomain": "1.3.6.1.2.1.47.1.2.1.1.6",
    "ENTITY-MIB::entLogicalContextEngineID": "1.3.6.1.2.1.47.1.2.1.1.7",
    "ENTITY-MIB::entLogicalContextName": "1.3.6.1.2.1.47.1.2.1.1.8",
    "ENTITY-MIB::entityMapping": "1.3.6.1.2.1.47.1.3",
    "ENTITY-MIB::entLPMappingTable": "1.3.6.1.2.1.47.1.3.1",
    "ENTITY-MIB::entLPMappingEntry": "1.3.6.1.2.1.47.1.3.1.1",
    "ENTITY-MIB::entLPPhysicalIndex": "1.3.6.1.2.1.47.1.3.1.1.1",
    "ENTITY-MIB::entAliasMappingTable": "1.3.6.1.2.1.47.1.3.2",
    "ENTITY-MIB::entAliasMappingEntry": "1.3.6.1.2.1.47.1.3.2.1",
    "ENTITY-MIB::entAliasLogicalIndexOrZero": "1.3.6.1.2.1.47.1.3.2.1.1",
    "ENTITY-MIB::entAliasMappingIdentifier": "1.3.6.1.2.1.47.1.3.2.1.2",
    "ENTITY-MIB::entPhysicalContainsTable": "1.3.6.1.2.1.47.1.3.3",
    "ENTITY-MIB::entPhysicalContainsEntry": "1.3.6.1.2.1.47.1.3.3.1",
    "ENTITY-MIB::entPhysicalChildIndex": "1.3.6.1.2.1.47.1.3.3.1.1",
    "ENTITY-MIB::entityGeneral": "1.3.6.1.2.1.47.1.4",
    "ENTITY-MIB::entLastChangeTime": "1.3.6.1.2.1.47.1.4.1",
    "ENTITY-MIB::entityMIBTraps": "1.3.6.1.2.1.47.2",
    "ENTITY-MIB::entityMIBTrapPrefix": "1.3.6.1.2.1.47.2.0",
    "ENTITY-MIB::entConfigChange": "1.3.6.1.2.1.47.2.0.1",
    "ENTITY-MIB::entityConformance": "1.3.6.1.2.1.47.3",
    "ENTITY-MIB::entityCompliances": "1.3.6.1.2.1.47.3.1",
    "ENTITY-MIB::entityGroups": "1.3.6.1.2.1.47.3.2"
}
