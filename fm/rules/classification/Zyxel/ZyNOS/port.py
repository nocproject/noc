# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel ZyNOS specific port rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.port import *
##
## Zyxel.ZyNOS Autonegotiation Has Failed SYSLOG
##
class Zyxel_ZyNOS_Autonegotiation_Failed_SYSLOG_Rule(ClassificationRule):
    name="Zyxel.ZyNOS Autonegatiation Failed SYSLOG"
    event_class=AutonegatiationFailed
    preference=1000
    patterns=[
        (r"^profile$",r"^Zyxel\.ZyNOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"switch: port (?P<interface>\S+) link speed and duplex mode autonegotiation has failed"),
    ]
