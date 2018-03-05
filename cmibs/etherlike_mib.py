# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# EtherLike-MIB
#     Compiled MIB
#     Do not modify this file directly
#     Run ./noc make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "EtherLike-MIB"
# Metadata
LAST_UPDATED = "2003-09-19"
COMPILED = "2018-02-11"
# MIB Data: name -> oid
MIB = {
    "EtherLike-MIB::dot3": "1.3.6.1.2.1.10.7",
    "EtherLike-MIB::dot3StatsTable": "1.3.6.1.2.1.10.7.2",
    "EtherLike-MIB::dot3StatsEntry": "1.3.6.1.2.1.10.7.2.1",
    "EtherLike-MIB::dot3StatsIndex": "1.3.6.1.2.1.10.7.2.1.1",
    "EtherLike-MIB::dot3StatsAlignmentErrors": "1.3.6.1.2.1.10.7.2.1.2",
    "EtherLike-MIB::dot3StatsFCSErrors": "1.3.6.1.2.1.10.7.2.1.3",
    "EtherLike-MIB::dot3StatsSingleCollisionFrames": "1.3.6.1.2.1.10.7.2.1.4",
    "EtherLike-MIB::dot3StatsMultipleCollisionFrames": "1.3.6.1.2.1.10.7.2.1.5",
    "EtherLike-MIB::dot3StatsSQETestErrors": "1.3.6.1.2.1.10.7.2.1.6",
    "EtherLike-MIB::dot3StatsDeferredTransmissions": "1.3.6.1.2.1.10.7.2.1.7",
    "EtherLike-MIB::dot3StatsLateCollisions": "1.3.6.1.2.1.10.7.2.1.8",
    "EtherLike-MIB::dot3StatsExcessiveCollisions": "1.3.6.1.2.1.10.7.2.1.9",
    "EtherLike-MIB::dot3StatsInternalMacTransmitErrors": "1.3.6.1.2.1.10.7.2.1.10",
    "EtherLike-MIB::dot3StatsCarrierSenseErrors": "1.3.6.1.2.1.10.7.2.1.11",
    "EtherLike-MIB::dot3StatsFrameTooLongs": "1.3.6.1.2.1.10.7.2.1.13",
    "EtherLike-MIB::dot3StatsInternalMacReceiveErrors": "1.3.6.1.2.1.10.7.2.1.16",
    "EtherLike-MIB::dot3StatsEtherChipSet": "1.3.6.1.2.1.10.7.2.1.17",
    "EtherLike-MIB::dot3StatsSymbolErrors": "1.3.6.1.2.1.10.7.2.1.18",
    "EtherLike-MIB::dot3StatsDuplexStatus": "1.3.6.1.2.1.10.7.2.1.19",
    "EtherLike-MIB::dot3StatsRateControlAbility": "1.3.6.1.2.1.10.7.2.1.20",
    "EtherLike-MIB::dot3StatsRateControlStatus": "1.3.6.1.2.1.10.7.2.1.21",
    "EtherLike-MIB::dot3CollTable": "1.3.6.1.2.1.10.7.5",
    "EtherLike-MIB::dot3CollEntry": "1.3.6.1.2.1.10.7.5.1",
    "EtherLike-MIB::dot3CollCount": "1.3.6.1.2.1.10.7.5.1.2",
    "EtherLike-MIB::dot3CollFrequencies": "1.3.6.1.2.1.10.7.5.1.3",
    "EtherLike-MIB::dot3Tests": "1.3.6.1.2.1.10.7.6",
    "EtherLike-MIB::dot3TestTdr": "1.3.6.1.2.1.10.7.6.1",
    "EtherLike-MIB::dot3TestLoopBack": "1.3.6.1.2.1.10.7.6.2",
    "EtherLike-MIB::dot3Errors": "1.3.6.1.2.1.10.7.7",
    "EtherLike-MIB::dot3ErrorInitError": "1.3.6.1.2.1.10.7.7.1",
    "EtherLike-MIB::dot3ErrorLoopbackError": "1.3.6.1.2.1.10.7.7.2",
    "EtherLike-MIB::dot3ControlTable": "1.3.6.1.2.1.10.7.9",
    "EtherLike-MIB::dot3ControlEntry": "1.3.6.1.2.1.10.7.9.1",
    "EtherLike-MIB::dot3ControlFunctionsSupported": "1.3.6.1.2.1.10.7.9.1.1",
    "EtherLike-MIB::dot3ControlInUnknownOpcodes": "1.3.6.1.2.1.10.7.9.1.2",
    "EtherLike-MIB::dot3HCControlInUnknownOpcodes": "1.3.6.1.2.1.10.7.9.1.3",
    "EtherLike-MIB::dot3PauseTable": "1.3.6.1.2.1.10.7.10",
    "EtherLike-MIB::dot3PauseEntry": "1.3.6.1.2.1.10.7.10.1",
    "EtherLike-MIB::dot3PauseAdminMode": "1.3.6.1.2.1.10.7.10.1.1",
    "EtherLike-MIB::dot3PauseOperMode": "1.3.6.1.2.1.10.7.10.1.2",
    "EtherLike-MIB::dot3InPauseFrames": "1.3.6.1.2.1.10.7.10.1.3",
    "EtherLike-MIB::dot3OutPauseFrames": "1.3.6.1.2.1.10.7.10.1.4",
    "EtherLike-MIB::dot3HCInPauseFrames": "1.3.6.1.2.1.10.7.10.1.5",
    "EtherLike-MIB::dot3HCOutPauseFrames": "1.3.6.1.2.1.10.7.10.1.6",
    "EtherLike-MIB::dot3HCStatsTable": "1.3.6.1.2.1.10.7.11",
    "EtherLike-MIB::dot3HCStatsEntry": "1.3.6.1.2.1.10.7.11.1",
    "EtherLike-MIB::dot3HCStatsAlignmentErrors": "1.3.6.1.2.1.10.7.11.1.1",
    "EtherLike-MIB::dot3HCStatsFCSErrors": "1.3.6.1.2.1.10.7.11.1.2",
    "EtherLike-MIB::dot3HCStatsInternalMacTransmitErrors": "1.3.6.1.2.1.10.7.11.1.3",
    "EtherLike-MIB::dot3HCStatsFrameTooLongs": "1.3.6.1.2.1.10.7.11.1.4",
    "EtherLike-MIB::dot3HCStatsInternalMacReceiveErrors": "1.3.6.1.2.1.10.7.11.1.5",
    "EtherLike-MIB::dot3HCStatsSymbolErrors": "1.3.6.1.2.1.10.7.11.1.6",
    "EtherLike-MIB::etherMIB": "1.3.6.1.2.1.35",
    "EtherLike-MIB::etherMIBObjects": "1.3.6.1.2.1.35.1",
    "EtherLike-MIB::etherConformance": "1.3.6.1.2.1.35.2",
    "EtherLike-MIB::etherGroups": "1.3.6.1.2.1.35.2.1",
    "EtherLike-MIB::etherCompliances": "1.3.6.1.2.1.35.2.2"
}
