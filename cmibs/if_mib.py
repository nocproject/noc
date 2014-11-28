# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IF-MIB
##    Compiled MIB
##    Do not modify this file directly
##    Run ./noc make-cmib instead
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# MIB Name
NAME = "IF-MIB"
# Metadata
LAST_UPDATED = "2000-06-14"
COMPILED = "2014-09-09"
# MIB Data: name -> oid
MIB = {
    "IF-MIB::interfaces": "1.3.6.1.2.1.2",
    "IF-MIB::ifNumber": "1.3.6.1.2.1.2.1",
    "IF-MIB::ifTable": "1.3.6.1.2.1.2.2",
    "IF-MIB::ifEntry": "1.3.6.1.2.1.2.2.1",
    "IF-MIB::ifIndex": "1.3.6.1.2.1.2.2.1.1",
    "IF-MIB::ifDescr": "1.3.6.1.2.1.2.2.1.2",
    "IF-MIB::ifType": "1.3.6.1.2.1.2.2.1.3",
    "IF-MIB::ifMtu": "1.3.6.1.2.1.2.2.1.4",
    "IF-MIB::ifSpeed": "1.3.6.1.2.1.2.2.1.5",
    "IF-MIB::ifPhysAddress": "1.3.6.1.2.1.2.2.1.6",
    "IF-MIB::ifAdminStatus": "1.3.6.1.2.1.2.2.1.7",
    "IF-MIB::ifOperStatus": "1.3.6.1.2.1.2.2.1.8",
    "IF-MIB::ifLastChange": "1.3.6.1.2.1.2.2.1.9",
    "IF-MIB::ifInOctets": "1.3.6.1.2.1.2.2.1.10",
    "IF-MIB::ifInUcastPkts": "1.3.6.1.2.1.2.2.1.11",
    "IF-MIB::ifInNUcastPkts": "1.3.6.1.2.1.2.2.1.12",
    "IF-MIB::ifInDiscards": "1.3.6.1.2.1.2.2.1.13",
    "IF-MIB::ifInErrors": "1.3.6.1.2.1.2.2.1.14",
    "IF-MIB::ifInUnknownProtos": "1.3.6.1.2.1.2.2.1.15",
    "IF-MIB::ifOutOctets": "1.3.6.1.2.1.2.2.1.16",
    "IF-MIB::ifOutUcastPkts": "1.3.6.1.2.1.2.2.1.17",
    "IF-MIB::ifOutNUcastPkts": "1.3.6.1.2.1.2.2.1.18",
    "IF-MIB::ifOutDiscards": "1.3.6.1.2.1.2.2.1.19",
    "IF-MIB::ifOutErrors": "1.3.6.1.2.1.2.2.1.20",
    "IF-MIB::ifOutQLen": "1.3.6.1.2.1.2.2.1.21",
    "IF-MIB::ifSpecific": "1.3.6.1.2.1.2.2.1.22",
    "IF-MIB::ifMIB": "1.3.6.1.2.1.31",
    "IF-MIB::ifMIBObjects": "1.3.6.1.2.1.31.1",
    "IF-MIB::ifXTable": "1.3.6.1.2.1.31.1.1",
    "IF-MIB::ifXEntry": "1.3.6.1.2.1.31.1.1.1",
    "IF-MIB::ifName": "1.3.6.1.2.1.31.1.1.1.1",
    "IF-MIB::ifInMulticastPkts": "1.3.6.1.2.1.31.1.1.1.2",
    "IF-MIB::ifInBroadcastPkts": "1.3.6.1.2.1.31.1.1.1.3",
    "IF-MIB::ifOutMulticastPkts": "1.3.6.1.2.1.31.1.1.1.4",
    "IF-MIB::ifOutBroadcastPkts": "1.3.6.1.2.1.31.1.1.1.5",
    "IF-MIB::ifHCInOctets": "1.3.6.1.2.1.31.1.1.1.6",
    "IF-MIB::ifHCInUcastPkts": "1.3.6.1.2.1.31.1.1.1.7",
    "IF-MIB::ifHCInMulticastPkts": "1.3.6.1.2.1.31.1.1.1.8",
    "IF-MIB::ifHCInBroadcastPkts": "1.3.6.1.2.1.31.1.1.1.9",
    "IF-MIB::ifHCOutOctets": "1.3.6.1.2.1.31.1.1.1.10",
    "IF-MIB::ifHCOutUcastPkts": "1.3.6.1.2.1.31.1.1.1.11",
    "IF-MIB::ifHCOutMulticastPkts": "1.3.6.1.2.1.31.1.1.1.12",
    "IF-MIB::ifHCOutBroadcastPkts": "1.3.6.1.2.1.31.1.1.1.13",
    "IF-MIB::ifLinkUpDownTrapEnable": "1.3.6.1.2.1.31.1.1.1.14",
    "IF-MIB::ifHighSpeed": "1.3.6.1.2.1.31.1.1.1.15",
    "IF-MIB::ifPromiscuousMode": "1.3.6.1.2.1.31.1.1.1.16",
    "IF-MIB::ifConnectorPresent": "1.3.6.1.2.1.31.1.1.1.17",
    "IF-MIB::ifAlias": "1.3.6.1.2.1.31.1.1.1.18",
    "IF-MIB::ifCounterDiscontinuityTime": "1.3.6.1.2.1.31.1.1.1.19",
    "IF-MIB::ifStackTable": "1.3.6.1.2.1.31.1.2",
    "IF-MIB::ifStackEntry": "1.3.6.1.2.1.31.1.2.1",
    "IF-MIB::ifStackHigherLayer": "1.3.6.1.2.1.31.1.2.1.1",
    "IF-MIB::ifStackLowerLayer": "1.3.6.1.2.1.31.1.2.1.2",
    "IF-MIB::ifStackStatus": "1.3.6.1.2.1.31.1.2.1.3",
    "IF-MIB::ifTestTable": "1.3.6.1.2.1.31.1.3",
    "IF-MIB::ifTestEntry": "1.3.6.1.2.1.31.1.3.1",
    "IF-MIB::ifTestId": "1.3.6.1.2.1.31.1.3.1.1",
    "IF-MIB::ifTestStatus": "1.3.6.1.2.1.31.1.3.1.2",
    "IF-MIB::ifTestType": "1.3.6.1.2.1.31.1.3.1.3",
    "IF-MIB::ifTestResult": "1.3.6.1.2.1.31.1.3.1.4",
    "IF-MIB::ifTestCode": "1.3.6.1.2.1.31.1.3.1.5",
    "IF-MIB::ifTestOwner": "1.3.6.1.2.1.31.1.3.1.6",
    "IF-MIB::ifRcvAddressTable": "1.3.6.1.2.1.31.1.4",
    "IF-MIB::ifRcvAddressEntry": "1.3.6.1.2.1.31.1.4.1",
    "IF-MIB::ifRcvAddressAddress": "1.3.6.1.2.1.31.1.4.1.1",
    "IF-MIB::ifRcvAddressStatus": "1.3.6.1.2.1.31.1.4.1.2",
    "IF-MIB::ifRcvAddressType": "1.3.6.1.2.1.31.1.4.1.3",
    "IF-MIB::ifTableLastChange": "1.3.6.1.2.1.31.1.5",
    "IF-MIB::ifStackLastChange": "1.3.6.1.2.1.31.1.6",
    "IF-MIB::ifConformance": "1.3.6.1.2.1.31.2",
    "IF-MIB::ifGroups": "1.3.6.1.2.1.31.2.1",
    "IF-MIB::ifCompliances": "1.3.6.1.2.1.31.2.2",
    "IF-MIB::linkDown": "1.3.6.1.6.3.1.1.5.3",
    "IF-MIB::linkUp": "1.3.6.1.6.3.1.1.5.4"
}
