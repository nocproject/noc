# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "CISCO-MAC-NOTIFICATION-MIB"

# Metadata
LAST_UPDATED = "2007-06-11"
COMPILED = "2024-11-24"

# MIB Data: name -> oid
MIB = {
    "CISCO-MAC-NOTIFICATION-MIB::ciscoMacNotificationMIB": "1.3.6.1.4.1.9.9.215",
    "CISCO-MAC-NOTIFICATION-MIB::ciscoMacNotificationMIBObjects": "1.3.6.1.4.1.9.9.215.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnGlobalObjects": "1.3.6.1.4.1.9.9.215.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnGlobalFeatureEnabled": "1.3.6.1.4.1.9.9.215.1.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnNotificationInterval": "1.3.6.1.4.1.9.9.215.1.1.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacAddressesLearnt": "1.3.6.1.4.1.9.9.215.1.1.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacAddressesRemoved": "1.3.6.1.4.1.9.9.215.1.1.4",
    "CISCO-MAC-NOTIFICATION-MIB::cmnNotificationsEnabled": "1.3.6.1.4.1.9.9.215.1.1.5",
    "CISCO-MAC-NOTIFICATION-MIB::cmnNotificationsSent": "1.3.6.1.4.1.9.9.215.1.1.6",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistTableMaxLength": "1.3.6.1.4.1.9.9.215.1.1.7",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistoryTable": "1.3.6.1.4.1.9.9.215.1.1.8",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistoryEntry": "1.3.6.1.4.1.9.9.215.1.1.8.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistIndex": "1.3.6.1.4.1.9.9.215.1.1.8.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistMacChangedMsg": "1.3.6.1.4.1.9.9.215.1.1.8.1.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnHistTimestamp": "1.3.6.1.4.1.9.9.215.1.1.8.1.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnInterfaceObjects": "1.3.6.1.4.1.9.9.215.1.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnIfConfigTable": "1.3.6.1.4.1.9.9.215.1.2.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnIfConfigEntry": "1.3.6.1.4.1.9.9.215.1.2.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacAddrLearntEnable": "1.3.6.1.4.1.9.9.215.1.2.1.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacAddrRemovedEnable": "1.3.6.1.4.1.9.9.215.1.2.1.1.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveObjects": "1.3.6.1.4.1.9.9.215.1.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveFeatureEnabled": "1.3.6.1.4.1.9.9.215.1.3.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveNotificationsEnabled": "1.3.6.1.4.1.9.9.215.1.3.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveAddress": "1.3.6.1.4.1.9.9.215.1.3.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveVlanNumber": "1.3.6.1.4.1.9.9.215.1.3.4",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveFromPortId": "1.3.6.1.4.1.9.9.215.1.3.5",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveToPortId": "1.3.6.1.4.1.9.9.215.1.3.6",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveTime": "1.3.6.1.4.1.9.9.215.1.3.7",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACThresholdObjects": "1.3.6.1.4.1.9.9.215.1.4",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACThresholdFeatureEnabled": "1.3.6.1.4.1.9.9.215.1.4.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACThresholdLimit": "1.3.6.1.4.1.9.9.215.1.4.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACThresholdInterval": "1.3.6.1.4.1.9.9.215.1.4.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMACThresholdNotifEnabled": "1.3.6.1.4.1.9.9.215.1.4.4",
    "CISCO-MAC-NOTIFICATION-MIB::cmnUtilizationTable": "1.3.6.1.4.1.9.9.215.1.4.5",
    "CISCO-MAC-NOTIFICATION-MIB::cmnUtilizationEntry": "1.3.6.1.4.1.9.9.215.1.4.5.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnUtilizationEntries": "1.3.6.1.4.1.9.9.215.1.4.5.1.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnUtilizationUtilization": "1.3.6.1.4.1.9.9.215.1.4.5.1.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnUtilizationTimeStamp": "1.3.6.1.4.1.9.9.215.1.4.5.1.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMIBNotificationPrefix": "1.3.6.1.4.1.9.9.215.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMIBNotifications": "1.3.6.1.4.1.9.9.215.2.0",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacChangedNotification": "1.3.6.1.4.1.9.9.215.2.0.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacMoveNotification": "1.3.6.1.4.1.9.9.215.2.0.2",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMacThresholdExceedNotif": "1.3.6.1.4.1.9.9.215.2.0.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMIBConformance": "1.3.6.1.4.1.9.9.215.3",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMIBCompliances": "1.3.6.1.4.1.9.9.215.3.1",
    "CISCO-MAC-NOTIFICATION-MIB::cmnMIBGroups": "1.3.6.1.4.1.9.9.215.3.2",
}

DISPLAY_HINTS = {
    "1.3.6.1.4.1.9.9.215.1.3.3": (
        "OctetString",
        "1x:",
    ),  # CISCO-MAC-NOTIFICATION-MIB::cmnMACMoveAddress
}
