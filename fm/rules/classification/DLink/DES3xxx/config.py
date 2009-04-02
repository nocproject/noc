# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DES3xxx Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.config import *

##
## DLink.DES3xxx Config Changed SYSLOG
##
class DLink_DES3xxx_Config_Changed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx Config Changed SYSLOG"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^source$", r"^syslog$"),
        (r"^profile$",r"^DLink\.DES3xxx$"),
        (r"^message$",r"INFO: Configuration"),
    ]
