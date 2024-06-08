# ----------------------------------------------------------------------
# NTPv4-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "NTPv4-MIB"

# Metadata
LAST_UPDATED = "2010-05-17"
COMPILED = "2024-04-05"

# MIB Data: name -> oid
MIB = {
    "NTPv4-MIB::ntpSnmpMIB": "1.3.6.1.2.1.197",
    "NTPv4-MIB::ntpEntNotifications": "1.3.6.1.2.1.197.0",
    "NTPv4-MIB::ntpEntNotifModeChange": "1.3.6.1.2.1.197.0.1",
    "NTPv4-MIB::ntpEntNotifStratumChange": "1.3.6.1.2.1.197.0.2",
    "NTPv4-MIB::ntpEntNotifSyspeerChanged": "1.3.6.1.2.1.197.0.3",
    "NTPv4-MIB::ntpEntNotifAddAssociation": "1.3.6.1.2.1.197.0.4",
    "NTPv4-MIB::ntpEntNotifRemoveAssociation": "1.3.6.1.2.1.197.0.5",
    "NTPv4-MIB::ntpEntNotifConfigChanged": "1.3.6.1.2.1.197.0.6",
    "NTPv4-MIB::ntpEntNotifLeapSecondAnnounced": "1.3.6.1.2.1.197.0.7",
    "NTPv4-MIB::ntpEntNotifHeartbeat": "1.3.6.1.2.1.197.0.8",
    "NTPv4-MIB::ntpSnmpMIBObjects": "1.3.6.1.2.1.197.1",
    "NTPv4-MIB::ntpEntInfo": "1.3.6.1.2.1.197.1.1",
    "NTPv4-MIB::ntpEntSoftwareName": "1.3.6.1.2.1.197.1.1.1",
    "NTPv4-MIB::ntpEntSoftwareVersion": "1.3.6.1.2.1.197.1.1.2",
    "NTPv4-MIB::ntpEntSoftwareVendor": "1.3.6.1.2.1.197.1.1.3",
    "NTPv4-MIB::ntpEntSystemType": "1.3.6.1.2.1.197.1.1.4",
    "NTPv4-MIB::ntpEntTimeResolution": "1.3.6.1.2.1.197.1.1.5",
    "NTPv4-MIB::ntpEntTimePrecision": "1.3.6.1.2.1.197.1.1.6",
    "NTPv4-MIB::ntpEntTimeDistance": "1.3.6.1.2.1.197.1.1.7",
    "NTPv4-MIB::ntpEntStatus": "1.3.6.1.2.1.197.1.2",
    "NTPv4-MIB::ntpEntStatusCurrentMode": "1.3.6.1.2.1.197.1.2.1",
    "NTPv4-MIB::ntpEntStatusStratum": "1.3.6.1.2.1.197.1.2.2",
    "NTPv4-MIB::ntpEntStatusActiveRefSourceId": "1.3.6.1.2.1.197.1.2.3",
    "NTPv4-MIB::ntpEntStatusActiveRefSourceName": "1.3.6.1.2.1.197.1.2.4",
    "NTPv4-MIB::ntpEntStatusActiveOffset": "1.3.6.1.2.1.197.1.2.5",
    "NTPv4-MIB::ntpEntStatusNumberOfRefSources": "1.3.6.1.2.1.197.1.2.6",
    "NTPv4-MIB::ntpEntStatusDispersion": "1.3.6.1.2.1.197.1.2.7",
    "NTPv4-MIB::ntpEntStatusEntityUptime": "1.3.6.1.2.1.197.1.2.8",
    "NTPv4-MIB::ntpEntStatusDateTime": "1.3.6.1.2.1.197.1.2.9",
    "NTPv4-MIB::ntpEntStatusLeapSecond": "1.3.6.1.2.1.197.1.2.10",
    "NTPv4-MIB::ntpEntStatusLeapSecDirection": "1.3.6.1.2.1.197.1.2.11",
    "NTPv4-MIB::ntpEntStatusInPkts": "1.3.6.1.2.1.197.1.2.12",
    "NTPv4-MIB::ntpEntStatusOutPkts": "1.3.6.1.2.1.197.1.2.13",
    "NTPv4-MIB::ntpEntStatusBadVersion": "1.3.6.1.2.1.197.1.2.14",
    "NTPv4-MIB::ntpEntStatusProtocolError": "1.3.6.1.2.1.197.1.2.15",
    "NTPv4-MIB::ntpEntStatusNotifications": "1.3.6.1.2.1.197.1.2.16",
    "NTPv4-MIB::ntpEntStatPktModeTable": "1.3.6.1.2.1.197.1.2.17",
    "NTPv4-MIB::ntpEntStatPktModeEntry": "1.3.6.1.2.1.197.1.2.17.1",
    "NTPv4-MIB::ntpEntStatPktMode": "1.3.6.1.2.1.197.1.2.17.1.1",
    "NTPv4-MIB::ntpEntStatPktSent": "1.3.6.1.2.1.197.1.2.17.1.2",
    "NTPv4-MIB::ntpEntStatPktReceived": "1.3.6.1.2.1.197.1.2.17.1.3",
    "NTPv4-MIB::ntpAssociation": "1.3.6.1.2.1.197.1.3",
    "NTPv4-MIB::ntpAssociationTable": "1.3.6.1.2.1.197.1.3.1",
    "NTPv4-MIB::ntpAssociationEntry": "1.3.6.1.2.1.197.1.3.1.1",
    "NTPv4-MIB::ntpAssocId": "1.3.6.1.2.1.197.1.3.1.1.1",
    "NTPv4-MIB::ntpAssocName": "1.3.6.1.2.1.197.1.3.1.1.2",
    "NTPv4-MIB::ntpAssocRefId": "1.3.6.1.2.1.197.1.3.1.1.3",
    "NTPv4-MIB::ntpAssocAddressType": "1.3.6.1.2.1.197.1.3.1.1.4",
    "NTPv4-MIB::ntpAssocAddress": "1.3.6.1.2.1.197.1.3.1.1.5",
    "NTPv4-MIB::ntpAssocOffset": "1.3.6.1.2.1.197.1.3.1.1.6",
    "NTPv4-MIB::ntpAssocStratum": "1.3.6.1.2.1.197.1.3.1.1.7",
    "NTPv4-MIB::ntpAssocStatusJitter": "1.3.6.1.2.1.197.1.3.1.1.8",
    "NTPv4-MIB::ntpAssocStatusDelay": "1.3.6.1.2.1.197.1.3.1.1.9",
    "NTPv4-MIB::ntpAssocStatusDispersion": "1.3.6.1.2.1.197.1.3.1.1.10",
    "NTPv4-MIB::ntpAssociationStatisticsTable": "1.3.6.1.2.1.197.1.3.2",
    "NTPv4-MIB::ntpAssociationStatisticsEntry": "1.3.6.1.2.1.197.1.3.2.1",
    "NTPv4-MIB::ntpAssocStatInPkts": "1.3.6.1.2.1.197.1.3.2.1.1",
    "NTPv4-MIB::ntpAssocStatOutPkts": "1.3.6.1.2.1.197.1.3.2.1.2",
    "NTPv4-MIB::ntpAssocStatProtocolError": "1.3.6.1.2.1.197.1.3.2.1.3",
    "NTPv4-MIB::ntpEntControl": "1.3.6.1.2.1.197.1.4",
    "NTPv4-MIB::ntpEntHeartbeatInterval": "1.3.6.1.2.1.197.1.4.1",
    "NTPv4-MIB::ntpEntNotifBits": "1.3.6.1.2.1.197.1.4.2",
    "NTPv4-MIB::ntpEntNotifObjects": "1.3.6.1.2.1.197.1.5",
    "NTPv4-MIB::ntpEntNotifMessage": "1.3.6.1.2.1.197.1.5.1",
    "NTPv4-MIB::ntpEntConformance": "1.3.6.1.2.1.197.2",
    "NTPv4-MIB::ntpEntCompliances": "1.3.6.1.2.1.197.2.1",
    "NTPv4-MIB::ntpEntGroups": "1.3.6.1.2.1.197.2.2",
}

DISPLAY_HINTS = {
    "1.3.6.1.2.1.197.1.2.2": ("Unsigned32", "d"),  # NTPv4-MIB::ntpEntStatusStratum
    "1.3.6.1.2.1.197.1.2.9": ("OctetString", "4d:4d:4d.4d"),  # NTPv4-MIB::ntpEntStatusDateTime
    "1.3.6.1.2.1.197.1.2.10": ("OctetString", "4d:4d:4d.4d"),  # NTPv4-MIB::ntpEntStatusLeapSecond
    "1.3.6.1.2.1.197.1.3.1.1.7": ("Unsigned32", "d"),  # NTPv4-MIB::ntpAssocStratum
}
