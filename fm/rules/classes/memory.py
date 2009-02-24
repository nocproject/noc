# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Memory-related events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Memory Allocation Error
##
class MemoryAllocationError(EventClass):
    name     = "Memory Allocation Error"
    category = "NETWORK"
    priority = "CRITICAL"
    subject_template="Memory allocation error"
    body_template="""Memory allocation error"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
