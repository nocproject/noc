# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 802.11 WI-FI events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## A station associated to an access point.
##
class Dot11Associated(EventClass):
    name="dot11 Associated"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station associated: {{mac}}"
    body_template="dot11 station associated: {{mac}}"
    class Vars:
        mac=Var(required=True)

##
## A station disassociated from an access point.
##
class Dot11Disassociated(EventClass):
    name="dot11 Disassociated"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station disassociated: {{mac}}"
    body_template="dot11 station disassociated: {{mac}}"
    class Vars:
        mac=Var(required=True)
##
## A station has roamed to a new access point.
##
class Dot11Roamed(EventClass):
    name="dot11 Roamed"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station roamed: {{mac}}"
    body_template="dot11 station roamed: {{mac}}"
    class Vars:
        mac=Var(required=True)
