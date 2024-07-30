# ----------------------------------------------------------------------
# JUNIPER-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "JUNIPER-MIB"

# Metadata
LAST_UPDATED = "2021-06-15"
COMPILED = "2024-06-27"

# MIB Data: name -> oid
MIB = {
    "JUNIPER-MIB::jnxAlarmPortInput": "1.3.6.1.4.1.2636.4.1.28",
    "JUNIPER-MIB::jnxBootFromBackup": "1.3.6.1.4.1.2636.4.1.16",
    "JUNIPER-MIB::jnxBoxAnatomy": "1.3.6.1.4.1.2636.3.1",
    "JUNIPER-MIB::jnxBoxClass": "1.3.6.1.4.1.2636.3.1.1",
    "JUNIPER-MIB::jnxBoxDescr": "1.3.6.1.4.1.2636.3.1.2",
    "JUNIPER-MIB::jnxBoxInstalled": "1.3.6.1.4.1.2636.3.1.5",
    "JUNIPER-MIB::jnxBoxKernelMemoryUsedPercent": "1.3.6.1.4.1.2636.3.1.16",
    "JUNIPER-MIB::jnxBoxPersonality": "1.3.6.1.4.1.2636.3.1.18",
    "JUNIPER-MIB::jnxBoxRevision": "1.3.6.1.4.1.2636.3.1.4",
    "JUNIPER-MIB::jnxBoxSerialNo": "1.3.6.1.4.1.2636.3.1.3",
    "JUNIPER-MIB::jnxBoxSystemDomainType": "1.3.6.1.4.1.2636.3.1.17",
    "JUNIPER-MIB::jnxContainersCount": "1.3.6.1.4.1.2636.3.1.6.1.7",
    "JUNIPER-MIB::jnxContainersDescr": "1.3.6.1.4.1.2636.3.1.6.1.6",
    "JUNIPER-MIB::jnxContainersEntry": "1.3.6.1.4.1.2636.3.1.6.1",
    "JUNIPER-MIB::jnxContainersIndex": "1.3.6.1.4.1.2636.3.1.6.1.1",
    "JUNIPER-MIB::jnxContainersLevel": "1.3.6.1.4.1.2636.3.1.6.1.3",
    "JUNIPER-MIB::jnxContainersTable": "1.3.6.1.4.1.2636.3.1.6",
    "JUNIPER-MIB::jnxContainersType": "1.3.6.1.4.1.2636.3.1.6.1.5",
    "JUNIPER-MIB::jnxContainersView": "1.3.6.1.4.1.2636.3.1.6.1.2",
    "JUNIPER-MIB::jnxContainersWithin": "1.3.6.1.4.1.2636.3.1.6.1.4",
    "JUNIPER-MIB::jnxContentsChassisCleiCode": "1.3.6.1.4.1.2636.3.1.8.1.13",
    "JUNIPER-MIB::jnxContentsChassisDescr": "1.3.6.1.4.1.2636.3.1.8.1.12",
    "JUNIPER-MIB::jnxContentsChassisId": "1.3.6.1.4.1.2636.3.1.8.1.11",
    "JUNIPER-MIB::jnxContentsContainerIndex": "1.3.6.1.4.1.2636.3.1.8.1.1",
    "JUNIPER-MIB::jnxContentsDescr": "1.3.6.1.4.1.2636.3.1.8.1.6",
    "JUNIPER-MIB::jnxContentsEntry": "1.3.6.1.4.1.2636.3.1.8.1",
    "JUNIPER-MIB::jnxContentsInstalled": "1.3.6.1.4.1.2636.3.1.8.1.9",
    "JUNIPER-MIB::jnxContentsL1Index": "1.3.6.1.4.1.2636.3.1.8.1.2",
    "JUNIPER-MIB::jnxContentsL2Index": "1.3.6.1.4.1.2636.3.1.8.1.3",
    "JUNIPER-MIB::jnxContentsL3Index": "1.3.6.1.4.1.2636.3.1.8.1.4",
    "JUNIPER-MIB::jnxContentsLastChange": "1.3.6.1.4.1.2636.3.1.7",
    "JUNIPER-MIB::jnxContentsModel": "1.3.6.1.4.1.2636.3.1.8.1.14",
    "JUNIPER-MIB::jnxContentsPartNo": "1.3.6.1.4.1.2636.3.1.8.1.10",
    "JUNIPER-MIB::jnxContentsRevision": "1.3.6.1.4.1.2636.3.1.8.1.8",
    "JUNIPER-MIB::jnxContentsSerialNo": "1.3.6.1.4.1.2636.3.1.8.1.7",
    "JUNIPER-MIB::jnxContentsTable": "1.3.6.1.4.1.2636.3.1.8",
    "JUNIPER-MIB::jnxContentsType": "1.3.6.1.4.1.2636.3.1.8.1.5",
    "JUNIPER-MIB::jnxExtSrcLockAcquired": "1.3.6.1.4.1.2636.4.2.5",
    "JUNIPER-MIB::jnxExtSrcLockLost": "1.3.6.1.4.1.2636.4.1.19",
    "JUNIPER-MIB::jnxFanFailure": "1.3.6.1.4.1.2636.4.1.2",
    "JUNIPER-MIB::jnxFanOK": "1.3.6.1.4.1.2636.4.2.2",
    "JUNIPER-MIB::jnxFEBSwitchover": "1.3.6.1.4.1.2636.4.1.13",
    "JUNIPER-MIB::jnxFilledChassisDescr": "1.3.6.1.4.1.2636.3.1.12.1.8",
    "JUNIPER-MIB::jnxFilledChassisId": "1.3.6.1.4.1.2636.3.1.12.1.7",
    "JUNIPER-MIB::jnxFilledContainerIndex": "1.3.6.1.4.1.2636.3.1.12.1.1",
    "JUNIPER-MIB::jnxFilledDescr": "1.3.6.1.4.1.2636.3.1.12.1.5",
    "JUNIPER-MIB::jnxFilledEntry": "1.3.6.1.4.1.2636.3.1.12.1",
    "JUNIPER-MIB::jnxFilledL1Index": "1.3.6.1.4.1.2636.3.1.12.1.2",
    "JUNIPER-MIB::jnxFilledL2Index": "1.3.6.1.4.1.2636.3.1.12.1.3",
    "JUNIPER-MIB::jnxFilledL3Index": "1.3.6.1.4.1.2636.3.1.12.1.4",
    "JUNIPER-MIB::jnxFilledLastChange": "1.3.6.1.4.1.2636.3.1.11",
    "JUNIPER-MIB::jnxFilledState": "1.3.6.1.4.1.2636.3.1.12.1.6",
    "JUNIPER-MIB::jnxFilledTable": "1.3.6.1.4.1.2636.3.1.12",
    "JUNIPER-MIB::jnxFmAsicErr": "1.3.6.1.4.1.2636.4.1.25",
    "JUNIPER-MIB::jnxFmCellDropErr": "1.3.6.1.4.1.2636.4.1.18",
    "JUNIPER-MIB::jnxFmHealthChkErr": "1.3.6.1.4.1.2636.4.1.27",
    "JUNIPER-MIB::jnxFmLinkErr": "1.3.6.1.4.1.2636.4.1.17",
    "JUNIPER-MIB::jnxFruChassisDescr": "1.3.6.1.4.1.2636.3.1.15.1.15",
    "JUNIPER-MIB::jnxFruChassisId": "1.3.6.1.4.1.2636.3.1.15.1.14",
    "JUNIPER-MIB::jnxFruCheck": "1.3.6.1.4.1.2636.4.1.12",
    "JUNIPER-MIB::jnxFruContentsIndex": "1.3.6.1.4.1.2636.3.1.15.1.1",
    "JUNIPER-MIB::jnxFruEntry": "1.3.6.1.4.1.2636.3.1.15.1",
    "JUNIPER-MIB::jnxFruFailed": "1.3.6.1.4.1.2636.4.1.9",
    "JUNIPER-MIB::jnxFruInsertion": "1.3.6.1.4.1.2636.4.1.6",
    "JUNIPER-MIB::jnxFruL1Index": "1.3.6.1.4.1.2636.3.1.15.1.2",
    "JUNIPER-MIB::jnxFruL2Index": "1.3.6.1.4.1.2636.3.1.15.1.3",
    "JUNIPER-MIB::jnxFruL3Index": "1.3.6.1.4.1.2636.3.1.15.1.4",
    "JUNIPER-MIB::jnxFruLastPowerOff": "1.3.6.1.4.1.2636.3.1.15.1.11",
    "JUNIPER-MIB::jnxFruLastPowerOn": "1.3.6.1.4.1.2636.3.1.15.1.12",
    "JUNIPER-MIB::jnxFruName": "1.3.6.1.4.1.2636.3.1.15.1.5",
    "JUNIPER-MIB::jnxFruOffline": "1.3.6.1.4.1.2636.4.1.10",
    "JUNIPER-MIB::jnxFruOfflineReason": "1.3.6.1.4.1.2636.3.1.15.1.10",
    "JUNIPER-MIB::jnxFruOK": "1.3.6.1.4.1.2636.4.2.4",
    "JUNIPER-MIB::jnxFruOnline": "1.3.6.1.4.1.2636.4.1.11",
    "JUNIPER-MIB::jnxFruPowerOff": "1.3.6.1.4.1.2636.4.1.7",
    "JUNIPER-MIB::jnxFruPowerOn": "1.3.6.1.4.1.2636.4.1.8",
    "JUNIPER-MIB::jnxFruPowerUpTime": "1.3.6.1.4.1.2636.3.1.15.1.13",
    "JUNIPER-MIB::jnxFruPsdAssignment": "1.3.6.1.4.1.2636.3.1.15.1.16",
    "JUNIPER-MIB::jnxFruRemoval": "1.3.6.1.4.1.2636.4.1.5",
    "JUNIPER-MIB::jnxFruSlot": "1.3.6.1.4.1.2636.3.1.15.1.7",
    "JUNIPER-MIB::jnxFruState": "1.3.6.1.4.1.2636.3.1.15.1.8",
    "JUNIPER-MIB::jnxFruTable": "1.3.6.1.4.1.2636.3.1.15",
    "JUNIPER-MIB::jnxFruTemp": "1.3.6.1.4.1.2636.3.1.15.1.9",
    "JUNIPER-MIB::jnxFruType": "1.3.6.1.4.1.2636.3.1.15.1.6",
    "JUNIPER-MIB::jnxHardDiskFailed": "1.3.6.1.4.1.2636.4.1.14",
    "JUNIPER-MIB::jnxHardDiskMissing": "1.3.6.1.4.1.2636.4.1.15",
    "JUNIPER-MIB::jnxHardDiskOK": "1.3.6.1.4.1.2636.4.2.6",
    "JUNIPER-MIB::jnxLEDAssociateIndex": "1.3.6.1.4.1.2636.3.1.10.1.2",
    "JUNIPER-MIB::jnxLEDAssociateTable": "1.3.6.1.4.1.2636.3.1.10.1.1",
    "JUNIPER-MIB::jnxLEDDescr": "1.3.6.1.4.1.2636.3.1.10.1.7",
    "JUNIPER-MIB::jnxLEDEntry": "1.3.6.1.4.1.2636.3.1.10.1",
    "JUNIPER-MIB::jnxLEDL1Index": "1.3.6.1.4.1.2636.3.1.10.1.3",
    "JUNIPER-MIB::jnxLEDL2Index": "1.3.6.1.4.1.2636.3.1.10.1.4",
    "JUNIPER-MIB::jnxLEDL3Index": "1.3.6.1.4.1.2636.3.1.10.1.5",
    "JUNIPER-MIB::jnxLEDLastChange": "1.3.6.1.4.1.2636.3.1.9",
    "JUNIPER-MIB::jnxLEDOriginator": "1.3.6.1.4.1.2636.3.1.10.1.6",
    "JUNIPER-MIB::jnxLEDState": "1.3.6.1.4.1.2636.3.1.10.1.8",
    "JUNIPER-MIB::jnxLEDStateOrdered": "1.3.6.1.4.1.2636.3.1.10.1.9",
    "JUNIPER-MIB::jnxLEDTable": "1.3.6.1.4.1.2636.3.1.10",
    "JUNIPER-MIB::jnxMountVarOffHardDiskFailed": "1.3.6.1.4.1.2636.4.1.26",
    "JUNIPER-MIB::jnxOperating15MinAvgCPU": "1.3.6.1.4.1.2636.3.1.13.1.25",
    "JUNIPER-MIB::jnxOperating15MinLoadAvg": "1.3.6.1.4.1.2636.3.1.13.1.22",
    "JUNIPER-MIB::jnxOperating1MinAvgCPU": "1.3.6.1.4.1.2636.3.1.13.1.23",
    "JUNIPER-MIB::jnxOperating1MinLoadAvg": "1.3.6.1.4.1.2636.3.1.13.1.20",
    "JUNIPER-MIB::jnxOperating5MinAvgCPU": "1.3.6.1.4.1.2636.3.1.13.1.24",
    "JUNIPER-MIB::jnxOperating5MinLoadAvg": "1.3.6.1.4.1.2636.3.1.13.1.21",
    "JUNIPER-MIB::jnxOperatingBuffer": "1.3.6.1.4.1.2636.3.1.13.1.11",
    "JUNIPER-MIB::jnxOperatingBufferCP": "1.3.6.1.4.1.2636.3.1.13.1.27",
    "JUNIPER-MIB::jnxOperatingBufferExt": "1.3.6.1.4.1.2636.3.1.13.1.29",
    "JUNIPER-MIB::jnxOperatingChassisDescr": "1.3.6.1.4.1.2636.3.1.13.1.18",
    "JUNIPER-MIB::jnxOperatingChassisId": "1.3.6.1.4.1.2636.3.1.13.1.17",
    "JUNIPER-MIB::jnxOperatingContentsIndex": "1.3.6.1.4.1.2636.3.1.13.1.1",
    "JUNIPER-MIB::jnxOperatingCPU": "1.3.6.1.4.1.2636.3.1.13.1.8",
    "JUNIPER-MIB::jnxOperatingDescr": "1.3.6.1.4.1.2636.3.1.13.1.5",
    "JUNIPER-MIB::jnxOperatingDRAMSize": "1.3.6.1.4.1.2636.3.1.13.1.10",
    "JUNIPER-MIB::jnxOperatingEntry": "1.3.6.1.4.1.2636.3.1.13.1",
    "JUNIPER-MIB::jnxOperatingFRUPower": "1.3.6.1.4.1.2636.3.1.13.1.26",
    "JUNIPER-MIB::jnxOperatingHeap": "1.3.6.1.4.1.2636.3.1.13.1.12",
    "JUNIPER-MIB::jnxOperatingISR": "1.3.6.1.4.1.2636.3.1.13.1.9",
    "JUNIPER-MIB::jnxOperatingL1Index": "1.3.6.1.4.1.2636.3.1.13.1.2",
    "JUNIPER-MIB::jnxOperatingL2Index": "1.3.6.1.4.1.2636.3.1.13.1.3",
    "JUNIPER-MIB::jnxOperatingL3Index": "1.3.6.1.4.1.2636.3.1.13.1.4",
    "JUNIPER-MIB::jnxOperatingLastRestart": "1.3.6.1.4.1.2636.3.1.13.1.14",
    "JUNIPER-MIB::jnxOperatingMemory": "1.3.6.1.4.1.2636.3.1.13.1.15",
    "JUNIPER-MIB::jnxOperatingMemoryCP": "1.3.6.1.4.1.2636.3.1.13.1.28",
    "JUNIPER-MIB::jnxOperatingRestartTime": "1.3.6.1.4.1.2636.3.1.13.1.19",
    "JUNIPER-MIB::jnxOperatingState": "1.3.6.1.4.1.2636.3.1.13.1.6",
    "JUNIPER-MIB::jnxOperatingStateOrdered": "1.3.6.1.4.1.2636.3.1.13.1.16",
    "JUNIPER-MIB::jnxOperatingTable": "1.3.6.1.4.1.2636.3.1.13",
    "JUNIPER-MIB::jnxOperatingTemp": "1.3.6.1.4.1.2636.3.1.13.1.7",
    "JUNIPER-MIB::jnxOperatingUpTime": "1.3.6.1.4.1.2636.3.1.13.1.13",
    "JUNIPER-MIB::jnxOverTemperature": "1.3.6.1.4.1.2636.4.1.3",
    "JUNIPER-MIB::jnxPlaneCheck": "1.3.6.1.4.1.2636.4.1.22",
    "JUNIPER-MIB::jnxPlaneFault": "1.3.6.1.4.1.2636.4.1.23",
    "JUNIPER-MIB::jnxPlaneOffline": "1.3.6.1.4.1.2636.4.1.20",
    "JUNIPER-MIB::jnxPlaneOnline": "1.3.6.1.4.1.2636.4.1.21",
    "JUNIPER-MIB::jnxPowerSupplyFailure": "1.3.6.1.4.1.2636.4.1.1",
    "JUNIPER-MIB::jnxPowerSupplyInputFailure": "1.3.6.1.4.1.2636.4.1.24",
    "JUNIPER-MIB::jnxPowerSupplyInputOK": "1.3.6.1.4.1.2636.4.2.7",
    "JUNIPER-MIB::jnxPowerSupplyOK": "1.3.6.1.4.1.2636.4.2.1",
    "JUNIPER-MIB::jnxRedundancyChassisDescr": "1.3.6.1.4.1.2636.3.1.14.1.16",
    "JUNIPER-MIB::jnxRedundancyChassisId": "1.3.6.1.4.1.2636.3.1.14.1.15",
    "JUNIPER-MIB::jnxRedundancyConfig": "1.3.6.1.4.1.2636.3.1.14.1.6",
    "JUNIPER-MIB::jnxRedundancyContentsIndex": "1.3.6.1.4.1.2636.3.1.14.1.1",
    "JUNIPER-MIB::jnxRedundancyDescr": "1.3.6.1.4.1.2636.3.1.14.1.5",
    "JUNIPER-MIB::jnxRedundancyEntry": "1.3.6.1.4.1.2636.3.1.14.1",
    "JUNIPER-MIB::jnxRedundancyKeepaliveElapsed": "1.3.6.1.4.1.2636.3.1.14.1.13",
    "JUNIPER-MIB::jnxRedundancyKeepaliveHeartbeat": "1.3.6.1.4.1.2636.3.1.14.1.11",
    "JUNIPER-MIB::jnxRedundancyKeepaliveLoss": "1.3.6.1.4.1.2636.3.1.14.1.14",
    "JUNIPER-MIB::jnxRedundancyKeepaliveTimeout": "1.3.6.1.4.1.2636.3.1.14.1.12",
    "JUNIPER-MIB::jnxRedundancyL1Index": "1.3.6.1.4.1.2636.3.1.14.1.2",
    "JUNIPER-MIB::jnxRedundancyL2Index": "1.3.6.1.4.1.2636.3.1.14.1.3",
    "JUNIPER-MIB::jnxRedundancyL3Index": "1.3.6.1.4.1.2636.3.1.14.1.4",
    "JUNIPER-MIB::jnxRedundancyState": "1.3.6.1.4.1.2636.3.1.14.1.7",
    "JUNIPER-MIB::jnxRedundancySwitchover": "1.3.6.1.4.1.2636.4.1.4",
    "JUNIPER-MIB::jnxRedundancySwitchoverCount": "1.3.6.1.4.1.2636.3.1.14.1.8",
    "JUNIPER-MIB::jnxRedundancySwitchoverReason": "1.3.6.1.4.1.2636.3.1.14.1.10",
    "JUNIPER-MIB::jnxRedundancySwitchoverTime": "1.3.6.1.4.1.2636.3.1.14.1.9",
    "JUNIPER-MIB::jnxRedundancyTable": "1.3.6.1.4.1.2636.3.1.14",
    "JUNIPER-MIB::jnxTemperatureOK": "1.3.6.1.4.1.2636.4.2.3",
    "JUNIPER-SMI::jnxChassisOKTraps": "1.3.6.1.4.1.2636.4.2",
    "JUNIPER-SMI::jnxChassisTraps": "1.3.6.1.4.1.2636.4.1",
    "JUNIPER-SMI::jnxMibs": "1.3.6.1.4.1.2636.3",
    "JUNIPER-SMI::jnxTraps": "1.3.6.1.4.1.2636.4",
    "JUNIPER-SMI::juniperMIB": "1.3.6.1.4.1.2636",
    "SNMPv2-SMI::dod": "1.3.6",
    "SNMPv2-SMI::enterprises": "1.3.6.1.4.1",
    "SNMPv2-SMI::internet": "1.3.6.1",
    "SNMPv2-SMI::iso": "1",
    "SNMPv2-SMI::org": "1.3",
    "SNMPv2-SMI::private": "1.3.6.1.4",
}

DISPLAY_HINTS = {}