# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link events classification
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.link import *

##
## SNMP Link Down
##
class SNMP_Link_Down_Rule(ClassificationRule):
    name="SNMP Link Down"
    event_class=LinkDown
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.3$"),
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.\d+$",r"(?P<interface>.*)"),
    ]
##
## SNMP Link Up
##
class SNMP_Link_Up_Rule(ClassificationRule):
    name="SNMP Link Up"
    event_class=LinkUp
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.4$"),
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.\d+$",r"(?P<interface>.*)"),
    ]
