# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS FreeBSD Memory-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.memory import *

##
## OS.FreeBSD MCA Memory Error SYSLOG
##
class OS_FreeBSD_MCA_Memory_Error_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD MCA Memory Error SYSLOG"
    event_class=MemoryAllocationError
    preference=1000
    patterns=[
        (r"^message$",r"MCA: Bank \d+, Status 0x\S+"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]

