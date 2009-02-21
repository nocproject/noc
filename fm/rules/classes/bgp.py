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
