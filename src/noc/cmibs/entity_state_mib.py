# ----------------------------------------------------------------------
# ENTITY-STATE-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "ENTITY-STATE-MIB"

# Metadata
LAST_UPDATED = "2005-11-22"
COMPILED = "2020-01-19"

# MIB Data: name -> oid
MIB = {
    "ENTITY-STATE-MIB::entityStateMIB": "1.3.6.1.2.1.131",
    "ENTITY-STATE-MIB::entStateNotifications": "1.3.6.1.2.1.131.0",
    "ENTITY-STATE-MIB::entStateOperEnabled": "1.3.6.1.2.1.131.0.1",
    "ENTITY-STATE-MIB::entStateOperDisabled": "1.3.6.1.2.1.131.0.2",
    "ENTITY-STATE-MIB::entStateObjects": "1.3.6.1.2.1.131.1",
    "ENTITY-STATE-MIB::entStateTable": "1.3.6.1.2.1.131.1.1",
    "ENTITY-STATE-MIB::entStateEntry": "1.3.6.1.2.1.131.1.1.1",
    "ENTITY-STATE-MIB::entStateLastChanged": "1.3.6.1.2.1.131.1.1.1.1",
    "ENTITY-STATE-MIB::entStateAdmin": "1.3.6.1.2.1.131.1.1.1.2",
    "ENTITY-STATE-MIB::entStateOper": "1.3.6.1.2.1.131.1.1.1.3",
    "ENTITY-STATE-MIB::entStateUsage": "1.3.6.1.2.1.131.1.1.1.4",
    "ENTITY-STATE-MIB::entStateAlarm": "1.3.6.1.2.1.131.1.1.1.5",
    "ENTITY-STATE-MIB::entStateStandby": "1.3.6.1.2.1.131.1.1.1.6",
    "ENTITY-STATE-MIB::entStateConformance": "1.3.6.1.2.1.131.2",
    "ENTITY-STATE-MIB::entStateCompliances": "1.3.6.1.2.1.131.2.1",
    "ENTITY-STATE-MIB::entStateGroups": "1.3.6.1.2.1.131.2.2",
}

DISPLAY_HINTS = {
    "1.3.6.1.2.1.131.1.1.1.1": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # ENTITY-STATE-MIB::entStateLastChanged
}
