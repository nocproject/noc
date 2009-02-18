# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Power-over-Ethernet events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## PoE Power Granted
##
class PoEPowerGranted(EventClass):
    name="PoE Power Granted"
    category="NETWORK"
    priority="NORMAL"
    subject_template="PoE Power Granted on {{interface}}"
    body_template="""PoE Power Granted on interface {{interface}}"""
    class Vars:
        interface=Var(required=True)
##
## PoE Power Disconnect
##
class PoEPowerDisconnect(EventClass):
    name="PoE Power Disconnect"
    category="NETWORK"
    priority="NORMAL"
    subject_template="PoE Power Disconnected on {{interface}}"
    body_template="""PoE Power Disconnected on interface {{interface}}"""
    class Vars:
        interface=Var(required=True)
