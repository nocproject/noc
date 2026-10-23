# ----------------------------------------------------------------------
# HOST-RESOURCES-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "HOST-RESOURCES-MIB"

# Metadata
LAST_UPDATED = "2000-03-06"
COMPILED = "2024-12-21"

# MIB Data: name -> oid
MIB = {
    "HOST-RESOURCES-MIB::host": "1.3.6.1.2.1.25",
    "HOST-RESOURCES-MIB::hrSystem": "1.3.6.1.2.1.25.1",
    "HOST-RESOURCES-MIB::hrSystemUptime": "1.3.6.1.2.1.25.1.1",
    "HOST-RESOURCES-MIB::hrSystemDate": "1.3.6.1.2.1.25.1.2",
    "HOST-RESOURCES-MIB::hrSystemInitialLoadDevice": "1.3.6.1.2.1.25.1.3",
    "HOST-RESOURCES-MIB::hrSystemInitialLoadParameters": "1.3.6.1.2.1.25.1.4",
    "HOST-RESOURCES-MIB::hrSystemNumUsers": "1.3.6.1.2.1.25.1.5",
    "HOST-RESOURCES-MIB::hrSystemProcesses": "1.3.6.1.2.1.25.1.6",
    "HOST-RESOURCES-MIB::hrSystemMaxProcesses": "1.3.6.1.2.1.25.1.7",
    "HOST-RESOURCES-MIB::hrStorage": "1.3.6.1.2.1.25.2",
    "HOST-RESOURCES-MIB::hrStorageTypes": "1.3.6.1.2.1.25.2.1",
    "HOST-RESOURCES-MIB::hrMemorySize": "1.3.6.1.2.1.25.2.2",
    "HOST-RESOURCES-MIB::hrStorageTable": "1.3.6.1.2.1.25.2.3",
    "HOST-RESOURCES-MIB::hrStorageEntry": "1.3.6.1.2.1.25.2.3.1",
    "HOST-RESOURCES-MIB::hrStorageIndex": "1.3.6.1.2.1.25.2.3.1.1",
    "HOST-RESOURCES-MIB::hrStorageType": "1.3.6.1.2.1.25.2.3.1.2",
    "HOST-RESOURCES-MIB::hrStorageDescr": "1.3.6.1.2.1.25.2.3.1.3",
    "HOST-RESOURCES-MIB::hrStorageAllocationUnits": "1.3.6.1.2.1.25.2.3.1.4",
    "HOST-RESOURCES-MIB::hrStorageSize": "1.3.6.1.2.1.25.2.3.1.5",
    "HOST-RESOURCES-MIB::hrStorageUsed": "1.3.6.1.2.1.25.2.3.1.6",
    "HOST-RESOURCES-MIB::hrStorageAllocationFailures": "1.3.6.1.2.1.25.2.3.1.7",
    "HOST-RESOURCES-MIB::hrDevice": "1.3.6.1.2.1.25.3",
    "HOST-RESOURCES-MIB::hrDeviceTypes": "1.3.6.1.2.1.25.3.1",
    "HOST-RESOURCES-MIB::hrDeviceTable": "1.3.6.1.2.1.25.3.2",
    "HOST-RESOURCES-MIB::hrDeviceEntry": "1.3.6.1.2.1.25.3.2.1",
    "HOST-RESOURCES-MIB::hrDeviceIndex": "1.3.6.1.2.1.25.3.2.1.1",
    "HOST-RESOURCES-MIB::hrDeviceType": "1.3.6.1.2.1.25.3.2.1.2",
    "HOST-RESOURCES-MIB::hrDeviceDescr": "1.3.6.1.2.1.25.3.2.1.3",
    "HOST-RESOURCES-MIB::hrDeviceID": "1.3.6.1.2.1.25.3.2.1.4",
    "HOST-RESOURCES-MIB::hrDeviceStatus": "1.3.6.1.2.1.25.3.2.1.5",
    "HOST-RESOURCES-MIB::hrDeviceErrors": "1.3.6.1.2.1.25.3.2.1.6",
    "HOST-RESOURCES-MIB::hrProcessorTable": "1.3.6.1.2.1.25.3.3",
    "HOST-RESOURCES-MIB::hrProcessorEntry": "1.3.6.1.2.1.25.3.3.1",
    "HOST-RESOURCES-MIB::hrProcessorFrwID": "1.3.6.1.2.1.25.3.3.1.1",
    "HOST-RESOURCES-MIB::hrProcessorLoad": "1.3.6.1.2.1.25.3.3.1.2",
    "HOST-RESOURCES-MIB::hrNetworkTable": "1.3.6.1.2.1.25.3.4",
    "HOST-RESOURCES-MIB::hrNetworkEntry": "1.3.6.1.2.1.25.3.4.1",
    "HOST-RESOURCES-MIB::hrNetworkIfIndex": "1.3.6.1.2.1.25.3.4.1.1",
    "HOST-RESOURCES-MIB::hrPrinterTable": "1.3.6.1.2.1.25.3.5",
    "HOST-RESOURCES-MIB::hrPrinterEntry": "1.3.6.1.2.1.25.3.5.1",
    "HOST-RESOURCES-MIB::hrPrinterStatus": "1.3.6.1.2.1.25.3.5.1.1",
    "HOST-RESOURCES-MIB::hrPrinterDetectedErrorState": "1.3.6.1.2.1.25.3.5.1.2",
    "HOST-RESOURCES-MIB::hrDiskStorageTable": "1.3.6.1.2.1.25.3.6",
    "HOST-RESOURCES-MIB::hrDiskStorageEntry": "1.3.6.1.2.1.25.3.6.1",
    "HOST-RESOURCES-MIB::hrDiskStorageAccess": "1.3.6.1.2.1.25.3.6.1.1",
    "HOST-RESOURCES-MIB::hrDiskStorageMedia": "1.3.6.1.2.1.25.3.6.1.2",
    "HOST-RESOURCES-MIB::hrDiskStorageRemoveble": "1.3.6.1.2.1.25.3.6.1.3",
    "HOST-RESOURCES-MIB::hrDiskStorageCapacity": "1.3.6.1.2.1.25.3.6.1.4",
    "HOST-RESOURCES-MIB::hrPartitionTable": "1.3.6.1.2.1.25.3.7",
    "HOST-RESOURCES-MIB::hrPartitionEntry": "1.3.6.1.2.1.25.3.7.1",
    "HOST-RESOURCES-MIB::hrPartitionIndex": "1.3.6.1.2.1.25.3.7.1.1",
    "HOST-RESOURCES-MIB::hrPartitionLabel": "1.3.6.1.2.1.25.3.7.1.2",
    "HOST-RESOURCES-MIB::hrPartitionID": "1.3.6.1.2.1.25.3.7.1.3",
    "HOST-RESOURCES-MIB::hrPartitionSize": "1.3.6.1.2.1.25.3.7.1.4",
    "HOST-RESOURCES-MIB::hrPartitionFSIndex": "1.3.6.1.2.1.25.3.7.1.5",
    "HOST-RESOURCES-MIB::hrFSTable": "1.3.6.1.2.1.25.3.8",
    "HOST-RESOURCES-MIB::hrFSEntry": "1.3.6.1.2.1.25.3.8.1",
    "HOST-RESOURCES-MIB::hrFSIndex": "1.3.6.1.2.1.25.3.8.1.1",
    "HOST-RESOURCES-MIB::hrFSMountPoint": "1.3.6.1.2.1.25.3.8.1.2",
    "HOST-RESOURCES-MIB::hrFSRemoteMountPoint": "1.3.6.1.2.1.25.3.8.1.3",
    "HOST-RESOURCES-MIB::hrFSType": "1.3.6.1.2.1.25.3.8.1.4",
    "HOST-RESOURCES-MIB::hrFSAccess": "1.3.6.1.2.1.25.3.8.1.5",
    "HOST-RESOURCES-MIB::hrFSBootable": "1.3.6.1.2.1.25.3.8.1.6",
    "HOST-RESOURCES-MIB::hrFSStorageIndex": "1.3.6.1.2.1.25.3.8.1.7",
    "HOST-RESOURCES-MIB::hrFSLastFullBackupDate": "1.3.6.1.2.1.25.3.8.1.8",
    "HOST-RESOURCES-MIB::hrFSLastPartialBackupDate": "1.3.6.1.2.1.25.3.8.1.9",
    "HOST-RESOURCES-MIB::hrFSTypes": "1.3.6.1.2.1.25.3.9",
    "HOST-RESOURCES-MIB::hrSWRun": "1.3.6.1.2.1.25.4",
    "HOST-RESOURCES-MIB::hrSWOSIndex": "1.3.6.1.2.1.25.4.1",
    "HOST-RESOURCES-MIB::hrSWRunTable": "1.3.6.1.2.1.25.4.2",
    "HOST-RESOURCES-MIB::hrSWRunEntry": "1.3.6.1.2.1.25.4.2.1",
    "HOST-RESOURCES-MIB::hrSWRunIndex": "1.3.6.1.2.1.25.4.2.1.1",
    "HOST-RESOURCES-MIB::hrSWRunName": "1.3.6.1.2.1.25.4.2.1.2",
    "HOST-RESOURCES-MIB::hrSWRunID": "1.3.6.1.2.1.25.4.2.1.3",
    "HOST-RESOURCES-MIB::hrSWRunPath": "1.3.6.1.2.1.25.4.2.1.4",
    "HOST-RESOURCES-MIB::hrSWRunParameters": "1.3.6.1.2.1.25.4.2.1.5",
    "HOST-RESOURCES-MIB::hrSWRunType": "1.3.6.1.2.1.25.4.2.1.6",
    "HOST-RESOURCES-MIB::hrSWRunStatus": "1.3.6.1.2.1.25.4.2.1.7",
    "HOST-RESOURCES-MIB::hrSWRunPerf": "1.3.6.1.2.1.25.5",
    "HOST-RESOURCES-MIB::hrSWRunPerfTable": "1.3.6.1.2.1.25.5.1",
    "HOST-RESOURCES-MIB::hrSWRunPerfEntry": "1.3.6.1.2.1.25.5.1.1",
    "HOST-RESOURCES-MIB::hrSWRunPerfCPU": "1.3.6.1.2.1.25.5.1.1.1",
    "HOST-RESOURCES-MIB::hrSWRunPerfMem": "1.3.6.1.2.1.25.5.1.1.2",
    "HOST-RESOURCES-MIB::hrSWInstalled": "1.3.6.1.2.1.25.6",
    "HOST-RESOURCES-MIB::hrSWInstalledLastChange": "1.3.6.1.2.1.25.6.1",
    "HOST-RESOURCES-MIB::hrSWInstalledLastUpdateTime": "1.3.6.1.2.1.25.6.2",
    "HOST-RESOURCES-MIB::hrSWInstalledTable": "1.3.6.1.2.1.25.6.3",
    "HOST-RESOURCES-MIB::hrSWInstalledEntry": "1.3.6.1.2.1.25.6.3.1",
    "HOST-RESOURCES-MIB::hrSWInstalledIndex": "1.3.6.1.2.1.25.6.3.1.1",
    "HOST-RESOURCES-MIB::hrSWInstalledName": "1.3.6.1.2.1.25.6.3.1.2",
    "HOST-RESOURCES-MIB::hrSWInstalledID": "1.3.6.1.2.1.25.6.3.1.3",
    "HOST-RESOURCES-MIB::hrSWInstalledType": "1.3.6.1.2.1.25.6.3.1.4",
    "HOST-RESOURCES-MIB::hrSWInstalledDate": "1.3.6.1.2.1.25.6.3.1.5",
    "HOST-RESOURCES-MIB::hrMIBAdminInfo": "1.3.6.1.2.1.25.7",
    "HOST-RESOURCES-MIB::hostResourcesMibModule": "1.3.6.1.2.1.25.7.1",
    "HOST-RESOURCES-MIB::hrMIBCompliances": "1.3.6.1.2.1.25.7.2",
    "HOST-RESOURCES-MIB::hrMIBGroups": "1.3.6.1.2.1.25.7.3",
}

DISPLAY_HINTS = {
    "1.3.6.1.2.1.25.1.2": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # HOST-RESOURCES-MIB::hrSystemDate
    "1.3.6.1.2.1.25.3.8.1.8": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # HOST-RESOURCES-MIB::hrFSLastFullBackupDate
    "1.3.6.1.2.1.25.3.8.1.9": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # HOST-RESOURCES-MIB::hrFSLastPartialBackupDate
    "1.3.6.1.2.1.25.6.3.1.5": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # HOST-RESOURCES-MIB::hrSWInstalledDate
}
