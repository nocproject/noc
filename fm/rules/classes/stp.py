# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Spanning-tree (STP) and variations (MST, RSTP, PVST+, etc) events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## STP Topology changed
##
class STPTopologyChange(EventClass):
    name="STP Topology Change"
    category="NETWORK"
    priority="MINOR"
    subject_template="STP Topology changed: {{interface}}"
    body_template="""STP Topology changed at interface {{interface}}"""
    class Vars:
        interface=Var(required=True)
