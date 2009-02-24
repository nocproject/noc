# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS VTP rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.port import *
##
## Cisco.IOS VTP Port Trunk Status Change SNMP
##
class Cisco_IOS_VTP_Port_Trunk_Status_Change_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS VTP Port Trunk Status Change SNMP"
    event_class=PortTrunkStatusChange
    preference=1000
    required_mibs=["CISCO-VTP-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.46\.2\.0\.7$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.46\.1\.6\.1\.1\.14\.(?P<ifindex>\d+)$",r"^(?P<status>\d+)$"),
    ]
