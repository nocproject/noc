# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco AireOS RADIUS classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.radius import *
##
## Cisco.AireOS RADIUS Dead SNMP
##
class Cisco_AireOS_RADIUS_Dead_SNMP_Rule(ClassificationRule):
    name="Cisco.AireOS RADIUS Dead SNMP"
    event_class=RADIUSDead
    preference=1000
    required_mibs=["CISCO-LWAPP-AAA-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.AireOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.598\.0\.5$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.598\.1\.2\.1\.1\.3\.\d+$",r"^(?P<ip>\S+)$"),
    ]
