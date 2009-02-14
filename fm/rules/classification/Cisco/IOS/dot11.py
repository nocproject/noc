# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS 802.11 classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.dot11 import *

##
## CISCO.IOS dot11 Associated
##
class CISCO_IOS_dot11_Associated_Rule(ClassificationRule):
    name="CISCO.IOS dot11 Associated"
    event_class=Dot11Associated
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-6-ASSOC:.+?(?P<mac>\S+) (?:A|Rea)ssociated"),
        (r"^profile$",r"^Cisco\.IOS$"),
    ]
##
## Cisco.IOS dot11 Disassociated
##
class Cisco_IOS_dot11_Disassociated_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Disassociated"
    event_class=Dot11Disassociated
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-6-DISASSOC: .+?(?P<mac>\S+) Reason"),
        (r"^profile$",r"^Cisco\.IOS$"),
    ]
