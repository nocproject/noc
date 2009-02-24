# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Process-related events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Process Traceback
##
class ProcessTraceback(EventClass):
    name     = "Process Traceback"
    category = "NETWORK"
    priority = "CRITICAL"
    subject_template="Process traceback: {{process}}"
    body_template="""Process crashed: {{process}}
PID: {{pid}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        pid=Var(required=False,repeat=False)
        process=Var(required=False,repeat=False)
