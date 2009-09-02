# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Power-over-Ethernet classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule, Expression
from noc.fm.rules.classes.phone import *
##
## Cisco.IOS Phone Call SNMP
##
class Cisco_IOS_Phone_Call_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Phone Call SNMP"
    event_class=PhoneCall
    preference=1000
    required_mibs=["DIAL-CONTROL-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.2\.1\.10\.21\.2\.0\.1$"),         # DIAL-CONTROL-MIB::dialCtlPeerCallInformation
        (r"^1\.3\.6\.1\.4\.1\.9\.10\.25\.1\.4\.3\.1\.5\.\d+$",r"^(?P<called_number>.+)$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.10\.25\.1\.4\.3\.1\.10\.\d+$",r"^(?P<connect_time>\d+)$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.10\.25\.1\.4\.3\.1\.8\.\d+$",r"(?P<call_clearing>\S+)"),
        (r"^1\.3\.6\.1\.4\.1\.9\.10\.25\.1\.4\.3\.1\.3\.\d+$",r"^(?P<calling_number>\S*)$"),   # Sometimes empty
        (r"^1\.3\.6\.1\.4\.1\.9\.10\.25\.1\.4\.3\.1\.11\.\d+$",r"^(?P<disconnect_time>\d+)$"),
        Expression("duration","int(disconnect_time)-int(connect_time)"),
    ]