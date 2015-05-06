# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMPv2-MIB
##    Compiled MIB
##    Do not modify this file directly
##    Run ./noc make-cmib instead
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# MIB Name
NAME = "SNMPv2-MIB"
# Metadata
LAST_UPDATED = "2002-10-16"
COMPILED = "2014-10-28"
# MIB Data: name -> oid
MIB = {
    "SNMPv2-MIB::system": "1.3.6.1.2.1.1",
    "SNMPv2-MIB::sysDescr": "1.3.6.1.2.1.1.1",
    "SNMPv2-MIB::sysObjectID": "1.3.6.1.2.1.1.2",
    "SNMPv2-MIB::sysUpTime": "1.3.6.1.2.1.1.3",
    "SNMPv2-MIB::sysContact": "1.3.6.1.2.1.1.4",
    "SNMPv2-MIB::sysName": "1.3.6.1.2.1.1.5",
    "SNMPv2-MIB::sysLocation": "1.3.6.1.2.1.1.6",
    "SNMPv2-MIB::sysServices": "1.3.6.1.2.1.1.7",
    "SNMPv2-MIB::sysORLastChange": "1.3.6.1.2.1.1.8",
    "SNMPv2-MIB::sysORTable": "1.3.6.1.2.1.1.9",
    "SNMPv2-MIB::sysOREntry": "1.3.6.1.2.1.1.9.1",
    "SNMPv2-MIB::sysORIndex": "1.3.6.1.2.1.1.9.1.1",
    "SNMPv2-MIB::sysORID": "1.3.6.1.2.1.1.9.1.2",
    "SNMPv2-MIB::sysORDescr": "1.3.6.1.2.1.1.9.1.3",
    "SNMPv2-MIB::sysORUpTime": "1.3.6.1.2.1.1.9.1.4",
    "SNMPv2-MIB::snmp": "1.3.6.1.2.1.11",
    "SNMPv2-MIB::snmpInPkts": "1.3.6.1.2.1.11.1",
    "SNMPv2-MIB::snmpOutPkts": "1.3.6.1.2.1.11.2",
    "SNMPv2-MIB::snmpInBadVersions": "1.3.6.1.2.1.11.3",
    "SNMPv2-MIB::snmpInBadCommunityNames": "1.3.6.1.2.1.11.4",
    "SNMPv2-MIB::snmpInBadCommunityUses": "1.3.6.1.2.1.11.5",
    "SNMPv2-MIB::snmpInASNParseErrs": "1.3.6.1.2.1.11.6",
    "SNMPv2-MIB::snmpInTooBigs": "1.3.6.1.2.1.11.8",
    "SNMPv2-MIB::snmpInNoSuchNames": "1.3.6.1.2.1.11.9",
    "SNMPv2-MIB::snmpInBadValues": "1.3.6.1.2.1.11.10",
    "SNMPv2-MIB::snmpInReadOnlys": "1.3.6.1.2.1.11.11",
    "SNMPv2-MIB::snmpInGenErrs": "1.3.6.1.2.1.11.12",
    "SNMPv2-MIB::snmpInTotalReqVars": "1.3.6.1.2.1.11.13",
    "SNMPv2-MIB::snmpInTotalSetVars": "1.3.6.1.2.1.11.14",
    "SNMPv2-MIB::snmpInGetRequests": "1.3.6.1.2.1.11.15",
    "SNMPv2-MIB::snmpInGetNexts": "1.3.6.1.2.1.11.16",
    "SNMPv2-MIB::snmpInSetRequests": "1.3.6.1.2.1.11.17",
    "SNMPv2-MIB::snmpInGetResponses": "1.3.6.1.2.1.11.18",
    "SNMPv2-MIB::snmpInTraps": "1.3.6.1.2.1.11.19",
    "SNMPv2-MIB::snmpOutTooBigs": "1.3.6.1.2.1.11.20",
    "SNMPv2-MIB::snmpOutNoSuchNames": "1.3.6.1.2.1.11.21",
    "SNMPv2-MIB::snmpOutBadValues": "1.3.6.1.2.1.11.22",
    "SNMPv2-MIB::snmpOutGenErrs": "1.3.6.1.2.1.11.24",
    "SNMPv2-MIB::snmpOutGetRequests": "1.3.6.1.2.1.11.25",
    "SNMPv2-MIB::snmpOutGetNexts": "1.3.6.1.2.1.11.26",
    "SNMPv2-MIB::snmpOutSetRequests": "1.3.6.1.2.1.11.27",
    "SNMPv2-MIB::snmpOutGetResponses": "1.3.6.1.2.1.11.28",
    "SNMPv2-MIB::snmpOutTraps": "1.3.6.1.2.1.11.29",
    "SNMPv2-MIB::snmpEnableAuthenTraps": "1.3.6.1.2.1.11.30",
    "SNMPv2-MIB::snmpSilentDrops": "1.3.6.1.2.1.11.31",
    "SNMPv2-MIB::snmpProxyDrops": "1.3.6.1.2.1.11.32",
    "SNMPv2-MIB::snmpMIB": "1.3.6.1.6.3.1",
    "SNMPv2-MIB::snmpMIBObjects": "1.3.6.1.6.3.1.1",
    "SNMPv2-MIB::snmpTrap": "1.3.6.1.6.3.1.1.4",
    "SNMPv2-MIB::snmpTrapOID": "1.3.6.1.6.3.1.1.4.1",
    "SNMPv2-MIB::snmpTrapEnterprise": "1.3.6.1.6.3.1.1.4.3",
    "SNMPv2-MIB::snmpTraps": "1.3.6.1.6.3.1.1.5",
    "SNMPv2-MIB::coldStart": "1.3.6.1.6.3.1.1.5.1",
    "SNMPv2-MIB::warmStart": "1.3.6.1.6.3.1.1.5.2",
    "SNMPv2-MIB::authenticationFailure": "1.3.6.1.6.3.1.1.5.5",
    "SNMPv2-MIB::snmpSet": "1.3.6.1.6.3.1.1.6",
    "SNMPv2-MIB::snmpSetSerialNo": "1.3.6.1.6.3.1.1.6.1",
    "SNMPv2-MIB::snmpMIBConformance": "1.3.6.1.6.3.1.2",
    "SNMPv2-MIB::snmpMIBCompliances": "1.3.6.1.6.3.1.2.1",
    "SNMPv2-MIB::snmpMIBGroups": "1.3.6.1.6.3.1.2.2"
}
