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
class Link_Down_SNMP_Rule(ClassificationRule):
    name="Link Down SNMP"
    event_class=LinkDown
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.3$"), # linkDown
        (r"^1\.3\.6\.1\.2\.1\.31\.1\.1\.1\.1\.\d+$",r"(?P<interface>.*)"),        # ifName
    ]
##
## SNMP Link Up
##
class Link_Up_SNMP_Rule(ClassificationRule):
    name="Link Up SNMP"
    event_class=LinkUp
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.4$"), # linkUp
        (r"^1\.3\.6\.1\.2\.1\.31\.1\.1\.1\.1\.\d+$",r"(?P<interface>.*)"),        # ifName
    ]
