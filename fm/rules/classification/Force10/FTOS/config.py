# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10 FTOS Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.config import *
##
## Force10.FTOS Config Changed SYSLOG
##
class Force10_FTOS_Config_Changed_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS Config Changed SYSLOG"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^message$",r"%FILEMGR-5-FILESAVED: Copied running-config to startup-config in \S+ by (?P<user>.*)$"),
        (r"^source$",r"^syslog$"),
    ]
