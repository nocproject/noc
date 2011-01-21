# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DxS Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.config import *

##
## DLink.DxS Config Changed SYSLOG
##
class DLink_DxS_Config_Changed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Config Changed SYSLOG"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^message$",r"Configuration"),
        (r"^source$", r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
