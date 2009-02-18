# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Power-over-Ethernet classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.poe import *
##
## Cisco.IOS PoE Power Granted Syslog
##
class Cisco_IOS_PoE_Power_Granted_Syslog_Rule(ClassificationRule):
    name="Cisco.IOS PoE Power Granted Syslog"
    event_class=PoEPowerGranted
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%ILPOWER-5-POWER_GRANTED: Interface (?P<interface>.+): Power granted$"),
    ]
##
## Cisco.IOS PoE Power Disconnect Syslog
##
class Cisco_IOS_PoE_Power_Disconnect_Syslog_Rule(ClassificationRule):
    name="Cisco.IOS PoE Power Disconnect Syslog"
    event_class=PoEPowerDisconnect
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r": %ILPOWER-5-IEEE_DISCONNECT: Interface (?P<interface>.+): PD removed$"),
    ]
