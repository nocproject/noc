# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Audiocodes Mediant2000 Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.config import *

##
## Audiocodes.Mediant2000 Config Changed SYSLOG
##
class Audiocodes_Mediant2000_Config_Changed_SYSLOG_Rule(ClassificationRule):
    name="Audiocodes.Mediant2000 Config Changed SYSLOG"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^profile$",r"^Audiocodes\.Mediant2000$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"User Name: (?P<user>.*?) ,Configuration file was burned to flash memory\. \[Code:80000003\]$"),
    ]
