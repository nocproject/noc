# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BGP4 classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.bgp import *
##
## BGP Backward Transition SNMP
##
class BGP_Backward_Transition_SNMP_Rule(ClassificationRule):
    name="BGP Backward Transition SNMP"
    event_class=BGPBackwardTransition
    preference=1000
    required_mibs=["BGP4-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.2\.1\.15\.3\.1\.2\.(?P<neighbor_ip>\S+)$",r"^(?P<state>\d+)$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.2\.1\.15\.7\.2$"),
    ]
