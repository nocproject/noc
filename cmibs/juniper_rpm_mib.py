# ----------------------------------------------------------------------
# JUNIPER-RPM-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "JUNIPER-RPM-MIB"

# Metadata
LAST_UPDATED = "2007-03-01"
COMPILED = "2021-06-26"

# MIB Data: name -> oid
MIB = {
    "JUNIPER-RPM-MIB::jnxRpmMib": "1.3.6.1.4.1.2636.3.50.1",
    "JUNIPER-RPM-MIB::jnxRpmResultsSampleTable": "1.3.6.1.4.1.2636.3.50.1.1",
    "JUNIPER-RPM-MIB::jnxRpmResultsSampleEntry": "1.3.6.1.4.1.2636.3.50.1.1.1",
    "JUNIPER-RPM-MIB::jnxRpmResSampleType": "1.3.6.1.4.1.2636.3.50.1.1.1.1",
    "JUNIPER-RPM-MIB::jnxRpmResSampleValue": "1.3.6.1.4.1.2636.3.50.1.1.1.2",
    "JUNIPER-RPM-MIB::jnxRpmResSampleTsType": "1.3.6.1.4.1.2636.3.50.1.1.1.3",
    "JUNIPER-RPM-MIB::jnxRpmResSampleDate": "1.3.6.1.4.1.2636.3.50.1.1.1.4",
    "JUNIPER-RPM-MIB::jnxRpmResultsSummaryTable": "1.3.6.1.4.1.2636.3.50.1.2",
    "JUNIPER-RPM-MIB::jnxRpmResultsSummaryEntry": "1.3.6.1.4.1.2636.3.50.1.2.1",
    "JUNIPER-RPM-MIB::jnxRpmResSumCollection": "1.3.6.1.4.1.2636.3.50.1.2.1.1",
    "JUNIPER-RPM-MIB::jnxRpmResSumSent": "1.3.6.1.4.1.2636.3.50.1.2.1.2",
    "JUNIPER-RPM-MIB::jnxRpmResSumReceived": "1.3.6.1.4.1.2636.3.50.1.2.1.3",
    "JUNIPER-RPM-MIB::jnxRpmResSumPercentLost": "1.3.6.1.4.1.2636.3.50.1.2.1.4",
    "JUNIPER-RPM-MIB::jnxRpmResSumDate": "1.3.6.1.4.1.2636.3.50.1.2.1.5",
    "JUNIPER-RPM-MIB::jnxRpmResultsCalculatedTable": "1.3.6.1.4.1.2636.3.50.1.3",
    "JUNIPER-RPM-MIB::jnxRpmResultsCalculatedEntry": "1.3.6.1.4.1.2636.3.50.1.3.1",
    "JUNIPER-RPM-MIB::jnxRpmResCalcSet": "1.3.6.1.4.1.2636.3.50.1.3.1.1",
    "JUNIPER-RPM-MIB::jnxRpmResCalcSamples": "1.3.6.1.4.1.2636.3.50.1.3.1.2",
    "JUNIPER-RPM-MIB::jnxRpmResCalcMin": "1.3.6.1.4.1.2636.3.50.1.3.1.3",
    "JUNIPER-RPM-MIB::jnxRpmResCalcMax": "1.3.6.1.4.1.2636.3.50.1.3.1.4",
    "JUNIPER-RPM-MIB::jnxRpmResCalcAverage": "1.3.6.1.4.1.2636.3.50.1.3.1.5",
    "JUNIPER-RPM-MIB::jnxRpmResCalcPkToPk": "1.3.6.1.4.1.2636.3.50.1.3.1.6",
    "JUNIPER-RPM-MIB::jnxRpmResCalcStdDev": "1.3.6.1.4.1.2636.3.50.1.3.1.7",
    "JUNIPER-RPM-MIB::jnxRpmResCalcSum": "1.3.6.1.4.1.2636.3.50.1.3.1.8",
    "JUNIPER-RPM-MIB::jnxRpmHistorySampleTable": "1.3.6.1.4.1.2636.3.50.1.4",
    "JUNIPER-RPM-MIB::jnxRpmHistorySampleEntry": "1.3.6.1.4.1.2636.3.50.1.4.1",
    "JUNIPER-RPM-MIB::jnxRpmHistSampleType": "1.3.6.1.4.1.2636.3.50.1.4.1.1",
    "JUNIPER-RPM-MIB::jnxRpmHistSampleValue": "1.3.6.1.4.1.2636.3.50.1.4.1.2",
    "JUNIPER-RPM-MIB::jnxRpmHistSampleTsType": "1.3.6.1.4.1.2636.3.50.1.4.1.3",
    "JUNIPER-RPM-MIB::jnxRpmHistorySummaryTable": "1.3.6.1.4.1.2636.3.50.1.5",
    "JUNIPER-RPM-MIB::jnxRpmHistorySummaryEntry": "1.3.6.1.4.1.2636.3.50.1.5.1",
    "JUNIPER-RPM-MIB::jnxRpmHistSumCollection": "1.3.6.1.4.1.2636.3.50.1.5.1.1",
    "JUNIPER-RPM-MIB::jnxRpmHistSumSent": "1.3.6.1.4.1.2636.3.50.1.5.1.2",
    "JUNIPER-RPM-MIB::jnxRpmHistSumReceived": "1.3.6.1.4.1.2636.3.50.1.5.1.3",
    "JUNIPER-RPM-MIB::jnxRpmHistSumPercentLost": "1.3.6.1.4.1.2636.3.50.1.5.1.4",
    "JUNIPER-RPM-MIB::jnxRpmHistoryCalculatedTable": "1.3.6.1.4.1.2636.3.50.1.6",
    "JUNIPER-RPM-MIB::jnxRpmHistoryCalculatedEntry": "1.3.6.1.4.1.2636.3.50.1.6.1",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcSet": "1.3.6.1.4.1.2636.3.50.1.6.1.1",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcSamples": "1.3.6.1.4.1.2636.3.50.1.6.1.2",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcMin": "1.3.6.1.4.1.2636.3.50.1.6.1.3",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcMax": "1.3.6.1.4.1.2636.3.50.1.6.1.4",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcAverage": "1.3.6.1.4.1.2636.3.50.1.6.1.5",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcPkToPk": "1.3.6.1.4.1.2636.3.50.1.6.1.6",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcStdDev": "1.3.6.1.4.1.2636.3.50.1.6.1.7",
    "JUNIPER-RPM-MIB::jnxRpmHistCalcSum": "1.3.6.1.4.1.2636.3.50.1.6.1.8",
}

DISPLAY_HINTS = {
    "1.3.6.1.4.1.2636.3.50.1.1.1.4": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # JUNIPER-RPM-MIB::jnxRpmResSampleDate
    "1.3.6.1.4.1.2636.3.50.1.2.1.5": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # JUNIPER-RPM-MIB::jnxRpmResSumDate
}
