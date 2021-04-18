# ----------------------------------------------------------------------
# DISMAN-PING-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "DISMAN-PING-MIB"

# Metadata
LAST_UPDATED = "2000-09-21"
COMPILED = "2021-04-16"

# MIB Data: name -> oid
MIB = {
    "DISMAN-PING-MIB::pingMIB": "1.3.6.1.2.1.80",
    "DISMAN-PING-MIB::pingNotifications": "1.3.6.1.2.1.80.0",
    "DISMAN-PING-MIB::pingProbeFailed": "1.3.6.1.2.1.80.0.1",
    "DISMAN-PING-MIB::pingTestFailed": "1.3.6.1.2.1.80.0.2",
    "DISMAN-PING-MIB::pingTestCompleted": "1.3.6.1.2.1.80.0.3",
    "DISMAN-PING-MIB::pingObjects": "1.3.6.1.2.1.80.1",
    "DISMAN-PING-MIB::pingMaxConcurrentRequests": "1.3.6.1.2.1.80.1.1",
    "DISMAN-PING-MIB::pingCtlTable": "1.3.6.1.2.1.80.1.2",
    "DISMAN-PING-MIB::pingCtlEntry": "1.3.6.1.2.1.80.1.2.1",
    "DISMAN-PING-MIB::pingCtlOwnerIndex": "1.3.6.1.2.1.80.1.2.1.1",
    "DISMAN-PING-MIB::pingCtlTestName": "1.3.6.1.2.1.80.1.2.1.2",
    "DISMAN-PING-MIB::pingCtlTargetAddressType": "1.3.6.1.2.1.80.1.2.1.3",
    "DISMAN-PING-MIB::pingCtlTargetAddress": "1.3.6.1.2.1.80.1.2.1.4",
    "DISMAN-PING-MIB::pingCtlDataSize": "1.3.6.1.2.1.80.1.2.1.5",
    "DISMAN-PING-MIB::pingCtlTimeOut": "1.3.6.1.2.1.80.1.2.1.6",
    "DISMAN-PING-MIB::pingCtlProbeCount": "1.3.6.1.2.1.80.1.2.1.7",
    "DISMAN-PING-MIB::pingCtlAdminStatus": "1.3.6.1.2.1.80.1.2.1.8",
    "DISMAN-PING-MIB::pingCtlDataFill": "1.3.6.1.2.1.80.1.2.1.9",
    "DISMAN-PING-MIB::pingCtlFrequency": "1.3.6.1.2.1.80.1.2.1.10",
    "DISMAN-PING-MIB::pingCtlMaxRows": "1.3.6.1.2.1.80.1.2.1.11",
    "DISMAN-PING-MIB::pingCtlStorageType": "1.3.6.1.2.1.80.1.2.1.12",
    "DISMAN-PING-MIB::pingCtlTrapGeneration": "1.3.6.1.2.1.80.1.2.1.13",
    "DISMAN-PING-MIB::pingCtlTrapProbeFailureFilter": "1.3.6.1.2.1.80.1.2.1.14",
    "DISMAN-PING-MIB::pingCtlTrapTestFailureFilter": "1.3.6.1.2.1.80.1.2.1.15",
    "DISMAN-PING-MIB::pingCtlType": "1.3.6.1.2.1.80.1.2.1.16",
    "DISMAN-PING-MIB::pingCtlDescr": "1.3.6.1.2.1.80.1.2.1.17",
    "DISMAN-PING-MIB::pingCtlSourceAddressType": "1.3.6.1.2.1.80.1.2.1.18",
    "DISMAN-PING-MIB::pingCtlSourceAddress": "1.3.6.1.2.1.80.1.2.1.19",
    "DISMAN-PING-MIB::pingCtlIfIndex": "1.3.6.1.2.1.80.1.2.1.20",
    "DISMAN-PING-MIB::pingCtlByPassRouteTable": "1.3.6.1.2.1.80.1.2.1.21",
    "DISMAN-PING-MIB::pingCtlDSField": "1.3.6.1.2.1.80.1.2.1.22",
    "DISMAN-PING-MIB::pingCtlRowStatus": "1.3.6.1.2.1.80.1.2.1.23",
    "DISMAN-PING-MIB::pingResultsTable": "1.3.6.1.2.1.80.1.3",
    "DISMAN-PING-MIB::pingResultsEntry": "1.3.6.1.2.1.80.1.3.1",
    "DISMAN-PING-MIB::pingResultsOperStatus": "1.3.6.1.2.1.80.1.3.1.1",
    "DISMAN-PING-MIB::pingResultsIpTargetAddressType": "1.3.6.1.2.1.80.1.3.1.2",
    "DISMAN-PING-MIB::pingResultsIpTargetAddress": "1.3.6.1.2.1.80.1.3.1.3",
    "DISMAN-PING-MIB::pingResultsMinRtt": "1.3.6.1.2.1.80.1.3.1.4",
    "DISMAN-PING-MIB::pingResultsMaxRtt": "1.3.6.1.2.1.80.1.3.1.5",
    "DISMAN-PING-MIB::pingResultsAverageRtt": "1.3.6.1.2.1.80.1.3.1.6",
    "DISMAN-PING-MIB::pingResultsProbeResponses": "1.3.6.1.2.1.80.1.3.1.7",
    "DISMAN-PING-MIB::pingResultsSentProbes": "1.3.6.1.2.1.80.1.3.1.8",
    "DISMAN-PING-MIB::pingResultsRttSumOfSquares": "1.3.6.1.2.1.80.1.3.1.9",
    "DISMAN-PING-MIB::pingResultsLastGoodProbe": "1.3.6.1.2.1.80.1.3.1.10",
    "DISMAN-PING-MIB::pingProbeHistoryTable": "1.3.6.1.2.1.80.1.4",
    "DISMAN-PING-MIB::pingProbeHistoryEntry": "1.3.6.1.2.1.80.1.4.1",
    "DISMAN-PING-MIB::pingProbeHistoryIndex": "1.3.6.1.2.1.80.1.4.1.1",
    "DISMAN-PING-MIB::pingProbeHistoryResponse": "1.3.6.1.2.1.80.1.4.1.2",
    "DISMAN-PING-MIB::pingProbeHistoryStatus": "1.3.6.1.2.1.80.1.4.1.3",
    "DISMAN-PING-MIB::pingProbeHistoryLastRC": "1.3.6.1.2.1.80.1.4.1.4",
    "DISMAN-PING-MIB::pingProbeHistoryTime": "1.3.6.1.2.1.80.1.4.1.5",
    "DISMAN-PING-MIB::pingConformance": "1.3.6.1.2.1.80.2",
    "DISMAN-PING-MIB::pingCompliances": "1.3.6.1.2.1.80.2.1",
    "DISMAN-PING-MIB::pingGroups": "1.3.6.1.2.1.80.2.2",
    "DISMAN-PING-MIB::pingImplementationTypeDomains": "1.3.6.1.2.1.80.3",
    "DISMAN-PING-MIB::pingIcmpEcho": "1.3.6.1.2.1.80.3.1",
    "DISMAN-PING-MIB::pingUdpEcho": "1.3.6.1.2.1.80.3.2",
    "DISMAN-PING-MIB::pingSnmpQuery": "1.3.6.1.2.1.80.3.3",
    "DISMAN-PING-MIB::pingTcpConnectionAttempt": "1.3.6.1.2.1.80.3.4",
}

DISPLAY_HINTS = {
    "1.3.6.1.2.1.80.1.2.1.17": ("OctetString", "255t"),  # DISMAN-PING-MIB::pingCtlDescr
    "1.3.6.1.2.1.80.1.3.1.10": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # DISMAN-PING-MIB::pingResultsLastGoodProbe
    "1.3.6.1.2.1.80.1.4.1.5": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # DISMAN-PING-MIB::pingProbeHistoryTime
}
