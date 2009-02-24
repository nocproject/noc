# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RADIUS events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## RADIUS Alive
##
class RADIUSAlive(EventClass):
    name     = "RADIUS Alive"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="Radius server responding: {{ip}}"
    body_template="""Radius server responding: {{ip}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=False)
##
## RADIUS Dead
##
class RADIUSDead(EventClass):
    name     = "RADIUS Dead"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="Radius server not responding: {{ip}}"
    body_template="""Radius server not responding: {{ip}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=False)
