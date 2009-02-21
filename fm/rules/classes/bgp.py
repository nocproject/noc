# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BGP events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
##
##
class BGPEstablished(EventClass):
    name = "BGP Established"
    category = "NETWORK"
    priority = "NORMAL"
    class Vars:
        neighbor_ip=Var(required=True)
##
## BGP Backward Transition
##
class BGPFSMStateChange(EventClass):
    name = "BGP FSM State Change"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="BGP Peer {{neighbor_ip}} state changed from {{from_state}} to {{to_state}}"
    body_template="""BGP Peer {{neighbor_ip}} changed state from {{from_state}} to {{to_state}}
    """
    class Vars:
        neighbor_ip=Var(required=True)
        from_state=Var(required=True)
        to_state=Var(required=True)
##
## BGP Backward Transition
##
class BGPBackwardTransition(EventClass):
    name = "BGP Backward Transition"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="BGP Peer backward transition: {{neighbor_ip}}"
    body_template="""BGP Peer {{neighbor_ip}} performs backward transition to state {{state}}
    """
    class Vars:
        neighbor_ip=Var(required=True)
        state=Var(required=True)
##
## BGP Max Prefixes Warning
##
class BGPMaxPrefixesWarning(EventClass):
    name     = "BGP Max Prefixes Warning"
    category = "NETWORK"
    priority = "WARNING"
    subject_template="BGP Prefixes warning: {{neighbor_ip}} ({{prefixes}}/{{max_prefixes}})"
    body_template="""Neighbor {{neighbor_ip}} reached {{prefixes}} prefixes with administrative limit of {{max_prefixes}}"""
    class Vars:
        neighbor_ip=Var(required=True)
        prefixes=Var(required=True)
        max_prefixes=Var(required=True)
