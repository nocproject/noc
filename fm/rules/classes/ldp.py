# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LDP events
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
#class LDPSessionUp(EventClass): pass
##
##
##
#class LDPSessionDown(EventClass): pass
##
##
##
class LDPLSPUp(EventClass):
    name="LDP LSP Up"
    category="NETWORK"
    priority="NORMAL"
    subject_template="LDP LSP Up: {{fec}}"
    body_template="""LDP LSP Up: {{fec}}"""
    class Vars:
        router_id=Var(required=True)
        fec=Var(required=True)
##
##
##
class LDPLSPDown(EventClass):
    name="LDP LSP Down"
    category="NETWORK"
    priority="MAJOR"
    subject_template="LDP LSP Down: {{fec}}"
    body_template="""LDP LSP Down: {{fec}}"""
    class Vars:
        router_id=Var(required=True)
        fec=Var(required=True)
