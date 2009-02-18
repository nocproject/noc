# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Spanning-tree (STP) and variations (MST, RSTP, PVST+, etc) rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.stp import *
##
## STP Topology Change SNMP
##
class STP_Topology_Change_SNMP_Rule(ClassificationRule):
    name="STP Topology Change SNMP"
    event_class=STPTopologyChange
    preference=1000
    required_mibs=["BRIDGE-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.2\.1\.17\.0\.2$"),
        (r"^1\.3\.6\.1\.2\.1\.31\.1\.1\.1\.1\.\d*$",r"(?P<interface>.+)"),
    ]