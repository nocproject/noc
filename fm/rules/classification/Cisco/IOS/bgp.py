# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS specific BGP rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.bgp import *
##
## Cisco.IOS BGP FSM State Change SNMP
##
class Cisco_IOS_BGP_FSM_State_Change_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS BGP FSM State Change SNMP"
    event_class=BGPFSMStateChange
    preference=1000
    required_mibs=["CISCO-BGP4-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),    
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.187\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.187\.1\.2\.1\.1\.8\.\S+$",r"^(?P<from_state>\d+)$"),
        (r"^1\.3\.6\.1\.2\.1\.15\.3\.1\.2\.(?P<neighbor_ip>\S+)$",r"^(?P<to_state>\d+)$"),
    ]

##
## Cisco.IOS BGP Backward Transition SNMP
##
class Cisco_IOS_BGP_Backward_Transition_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS BGP Backward Transition SNMP"
    event_class=BGPBackwardTransition
    preference=1000
    required_mibs=["CISCO-BGP4-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.2\.1\.15\.3\.1\.2\.(?P<neighbor_ip>\S+)$",r"^(?P<state>\d+)$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.187\.0\.2$"),
    ]
##
## Cisco.IOS BGP Max Prefixes Warning SYSLOG SNMP
##
class Cisco_IOS_BGP_Max_Prefixes_Warning_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS BGP Max Prefixes Warning SYSLOG SNMP"
    event_class=BGPMaxPrefixesWarning
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^MAXPFX$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^No\. of prefix received from (?P<neighbor_ip>\S+).*reaches (?P<prefixes>\d+), max (?P<max_prefixes>\d+)$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^BGP$"),
    ]
