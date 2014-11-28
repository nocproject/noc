# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CISCO-PPPOE-MIB
##    Compiled MIB
##    Do not modify this file directly
##    Run ./noc make-cmib instead
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# MIB Name
NAME = "CISCO-PPPOE-MIB"
# Metadata
LAST_UPDATED = "2011-04-25"
COMPILED = "2014-11-21"
# MIB Data: name -> oid
MIB = {
    "CISCO-PPPOE-MIB::ciscoPppoeMIB": "1.3.6.1.4.1.9.9.194",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBObjects": "1.3.6.1.4.1.9.9.194.1",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionInfo": "1.3.6.1.4.1.9.9.194.1.1",
    "CISCO-PPPOE-MIB::cPppoeSystemCurrSessions": "1.3.6.1.4.1.9.9.194.1.1.1",
    "CISCO-PPPOE-MIB::cPppoeSystemHighWaterSessions": "1.3.6.1.4.1.9.9.194.1.1.2",
    "CISCO-PPPOE-MIB::cPppoeSystemMaxAllowedSessions": "1.3.6.1.4.1.9.9.194.1.1.3",
    "CISCO-PPPOE-MIB::cPppoeSystemThresholdSessions": "1.3.6.1.4.1.9.9.194.1.1.4",
    "CISCO-PPPOE-MIB::cPppoeSystemExceededSessionErrors": "1.3.6.1.4.1.9.9.194.1.1.5",
    "CISCO-PPPOE-MIB::cPppoeSystemPerMacSessionlimit": "1.3.6.1.4.1.9.9.194.1.1.6",
    "CISCO-PPPOE-MIB::cPppoeSystemPerMacIWFSessionlimit": "1.3.6.1.4.1.9.9.194.1.1.7",
    "CISCO-PPPOE-MIB::cPppoeSystemPerMacThrottleRatelimit": "1.3.6.1.4.1.9.9.194.1.1.8",
    "CISCO-PPPOE-MIB::cPppoeSystemPerVLANlimit": "1.3.6.1.4.1.9.9.194.1.1.9",
    "CISCO-PPPOE-MIB::cPppoeSystemPerVLANthrottleRatelimit": "1.3.6.1.4.1.9.9.194.1.1.10",
    "CISCO-PPPOE-MIB::cPppoeSystemPerVClimit": "1.3.6.1.4.1.9.9.194.1.1.11",
    "CISCO-PPPOE-MIB::cPppoeSystemPerVCThrottleRatelimit": "1.3.6.1.4.1.9.9.194.1.1.12",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionLossThreshold": "1.3.6.1.4.1.9.9.194.1.1.13",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionLossPercent": "1.3.6.1.4.1.9.9.194.1.1.14",
    "CISCO-PPPOE-MIB::cPppoeVcCfgInfo": "1.3.6.1.4.1.9.9.194.1.2",
    "CISCO-PPPOE-MIB::cPppoeVcCfgTable": "1.3.6.1.4.1.9.9.194.1.2.1",
    "CISCO-PPPOE-MIB::cPppoeVcCfgEntry": "1.3.6.1.4.1.9.9.194.1.2.1.1",
    "CISCO-PPPOE-MIB::cPppoeVcEnable": "1.3.6.1.4.1.9.9.194.1.2.1.1.1",
    "CISCO-PPPOE-MIB::cPppoeVcSessionsInfo": "1.3.6.1.4.1.9.9.194.1.3",
    "CISCO-PPPOE-MIB::cPppoeVcSessionsTable": "1.3.6.1.4.1.9.9.194.1.3.1",
    "CISCO-PPPOE-MIB::cPppoeVcSessionsEntry": "1.3.6.1.4.1.9.9.194.1.3.1.1",
    "CISCO-PPPOE-MIB::cPppoeVcCurrSessions": "1.3.6.1.4.1.9.9.194.1.3.1.1.1",
    "CISCO-PPPOE-MIB::cPppoeVcHighWaterSessions": "1.3.6.1.4.1.9.9.194.1.3.1.1.2",
    "CISCO-PPPOE-MIB::cPppoeVcMaxAllowedSessions": "1.3.6.1.4.1.9.9.194.1.3.1.1.3",
    "CISCO-PPPOE-MIB::cPppoeVcThresholdSessions": "1.3.6.1.4.1.9.9.194.1.3.1.1.4",
    "CISCO-PPPOE-MIB::cPppoeVcExceededSessionErrors": "1.3.6.1.4.1.9.9.194.1.3.1.1.5",
    "CISCO-PPPOE-MIB::cPppoeSessionsPerInterfaceInfo": "1.3.6.1.4.1.9.9.194.1.4",
    "CISCO-PPPOE-MIB::cPppoeSessionsPerInterfaceTable": "1.3.6.1.4.1.9.9.194.1.4.1",
    "CISCO-PPPOE-MIB::cPppoeSessionsPerInterfaceEntry": "1.3.6.1.4.1.9.9.194.1.4.1.1",
    "CISCO-PPPOE-MIB::cPppoeTotalSessions": "1.3.6.1.4.1.9.9.194.1.4.1.1.1",
    "CISCO-PPPOE-MIB::cPppoePtaSessions": "1.3.6.1.4.1.9.9.194.1.4.1.1.2",
    "CISCO-PPPOE-MIB::cPppoeFwdedSessions": "1.3.6.1.4.1.9.9.194.1.4.1.1.3",
    "CISCO-PPPOE-MIB::cPppoeTransSessions": "1.3.6.1.4.1.9.9.194.1.4.1.1.4",
    "CISCO-PPPOE-MIB::cPppoePerInterfaceSessionLossThreshold": "1.3.6.1.4.1.9.9.194.1.4.1.1.5",
    "CISCO-PPPOE-MIB::cPppoePerInterfaceSessionLossPercent": "1.3.6.1.4.1.9.9.194.1.4.1.1.6",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionNotifyObjects": "1.3.6.1.4.1.9.9.194.1.5",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionClientMacAddress": "1.3.6.1.4.1.9.9.194.1.5.1",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionVlanID": "1.3.6.1.4.1.9.9.194.1.5.2",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionInnerVlanID": "1.3.6.1.4.1.9.9.194.1.5.3",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionVci": "1.3.6.1.4.1.9.9.194.1.5.4",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionVpi": "1.3.6.1.4.1.9.9.194.1.5.5",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBNotificationPrefix": "1.3.6.1.4.1.9.9.194.2",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBNotification": "1.3.6.1.4.1.9.9.194.2.0",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionThresholdTrap": "1.3.6.1.4.1.9.9.194.2.0.1",
    "CISCO-PPPOE-MIB::cPppoeVcSessionThresholdTrap": "1.3.6.1.4.1.9.9.194.2.0.2",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerMACLimitNotif": "1.3.6.1.4.1.9.9.194.2.0.3",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerMACThrottleNotif": "1.3.6.1.4.1.9.9.194.2.0.4",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerVLANLimitNotif": "1.3.6.1.4.1.9.9.194.2.0.5",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerVLANThrottleNotif": "1.3.6.1.4.1.9.9.194.2.0.6",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerVCLimitNotif": "1.3.6.1.4.1.9.9.194.2.0.7",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionPerVCThrottleNotif": "1.3.6.1.4.1.9.9.194.2.0.8",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionLossThresholdNotif": "1.3.6.1.4.1.9.9.194.2.0.9",
    "CISCO-PPPOE-MIB::cPppoePerInterfaceSessionLossThresholdNotif": "1.3.6.1.4.1.9.9.194.2.0.10",
    "CISCO-PPPOE-MIB::cPppoeSystemSessionLossPercentNotif": "1.3.6.1.4.1.9.9.194.2.0.11",
    "CISCO-PPPOE-MIB::cPppoePerInterfaceSessionLossPercentNotif": "1.3.6.1.4.1.9.9.194.2.0.12",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBConformance": "1.3.6.1.4.1.9.9.194.3",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBCompliances": "1.3.6.1.4.1.9.9.194.3.1",
    "CISCO-PPPOE-MIB::ciscoPppoeMIBGroups": "1.3.6.1.4.1.9.9.194.3.2"
}
