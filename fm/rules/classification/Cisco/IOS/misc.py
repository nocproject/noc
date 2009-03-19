# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS miscellaneous rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,DROP_EVENT
from noc.fm.rules.classes.default import DROP
##
## Cisco.IOS TCP Connection Closed
##
class Cisco_IOS_TCP_Connection_Closed_Rule(ClassificationRule):
    name="Cisco.IOS TCP Connection Closed"
    event_class=DROP
    preference=90000
    action=DROP_EVENT
    required_mibs=["CISCOTRAP-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.0\.1$"),
        (r"^profile$",r"^Cisco\.IOS$"),
    ]
