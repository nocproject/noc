# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CISCO-VLAN-MEMBERSHIP-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc mib make_cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "CISCO-VLAN-MEMBERSHIP-MIB"
# Metadata
LAST_UPDATED = "2007-12-14"
COMPILED = "2018-06-09"
# MIB Data: name -> oid
MIB = {
    "CISCO-VLAN-MEMBERSHIP-MIB::ciscoVlanMembershipMIB": "1.3.6.1.4.1.9.9.68",
    "CISCO-VLAN-MEMBERSHIP-MIB::ciscoVlanMembershipMIBObjects": "1.3.6.1.4.1.9.9.68.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmps": "1.3.6.1.4.1.9.9.68.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsVQPVersion": "1.3.6.1.4.1.9.9.68.1.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsRetries": "1.3.6.1.4.1.9.9.68.1.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsReconfirmInterval": "1.3.6.1.4.1.9.9.68.1.1.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsReconfirm": "1.3.6.1.4.1.9.9.68.1.1.4",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsReconfirmResult": "1.3.6.1.4.1.9.9.68.1.1.5",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsCurrent": "1.3.6.1.4.1.9.9.68.1.1.6",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsTable": "1.3.6.1.4.1.9.9.68.1.1.7",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsEntry": "1.3.6.1.4.1.9.9.68.1.1.7.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsIpAddress": "1.3.6.1.4.1.9.9.68.1.1.7.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsPrimary": "1.3.6.1.4.1.9.9.68.1.1.7.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsRowStatus": "1.3.6.1.4.1.9.9.68.1.1.7.1.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembership": "1.3.6.1.4.1.9.9.68.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryTable": "1.3.6.1.4.1.9.9.68.1.2.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryEntry": "1.3.6.1.4.1.9.9.68.1.2.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryVlanIndex": "1.3.6.1.4.1.9.9.68.1.2.1.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryMemberPorts": "1.3.6.1.4.1.9.9.68.1.2.1.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryMember2kPorts": "1.3.6.1.4.1.9.9.68.1.2.1.1.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipTable": "1.3.6.1.4.1.9.9.68.1.2.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipEntry": "1.3.6.1.4.1.9.9.68.1.2.2.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlanType": "1.3.6.1.4.1.9.9.68.1.2.2.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlan": "1.3.6.1.4.1.9.9.68.1.2.2.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmPortStatus": "1.3.6.1.4.1.9.9.68.1.2.2.1.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlans": "1.3.6.1.4.1.9.9.68.1.2.2.1.4",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlans2k": "1.3.6.1.4.1.9.9.68.1.2.2.1.5",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlans3k": "1.3.6.1.4.1.9.9.68.1.2.2.1.6",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlans4k": "1.3.6.1.4.1.9.9.68.1.2.2.1.7",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryExtTable": "1.3.6.1.4.1.9.9.68.1.2.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryExtEntry": "1.3.6.1.4.1.9.9.68.1.2.3.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipPortRangeIndex": "1.3.6.1.4.1.9.9.68.1.2.3.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMembershipSummaryExtPorts": "1.3.6.1.4.1.9.9.68.1.2.3.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVlanCreationMode": "1.3.6.1.4.1.9.9.68.1.2.4",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmStatistics": "1.3.6.1.4.1.9.9.68.1.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPQueries": "1.3.6.1.4.1.9.9.68.1.3.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPResponses": "1.3.6.1.4.1.9.9.68.1.3.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsChanges": "1.3.6.1.4.1.9.9.68.1.3.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPShutdown": "1.3.6.1.4.1.9.9.68.1.3.4",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPDenied": "1.3.6.1.4.1.9.9.68.1.3.5",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPWrongDomain": "1.3.6.1.4.1.9.9.68.1.3.6",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVQPWrongVersion": "1.3.6.1.4.1.9.9.68.1.3.7",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmInsufficientResources": "1.3.6.1.4.1.9.9.68.1.3.8",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmStatus": "1.3.6.1.4.1.9.9.68.1.4",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmNotificationsEnabled": "1.3.6.1.4.1.9.9.68.1.4.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVoiceVlan": "1.3.6.1.4.1.9.9.68.1.5",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVoiceVlanTable": "1.3.6.1.4.1.9.9.68.1.5.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVoiceVlanEntry": "1.3.6.1.4.1.9.9.68.1.5.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVoiceVlanId": "1.3.6.1.4.1.9.9.68.1.5.1.1.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVoiceVlanCdpVerifyEnable": "1.3.6.1.4.1.9.9.68.1.5.1.1.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmNotifications": "1.3.6.1.4.1.9.9.68.2",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmNotificationsPrefix": "1.3.6.1.4.1.9.9.68.2.0",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmVmpsChange": "1.3.6.1.4.1.9.9.68.2.0.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMIBConformance": "1.3.6.1.4.1.9.9.68.3",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMIBCompliances": "1.3.6.1.4.1.9.9.68.3.1",
    "CISCO-VLAN-MEMBERSHIP-MIB::vmMIBGroups": "1.3.6.1.4.1.9.9.68.3.2"
}
