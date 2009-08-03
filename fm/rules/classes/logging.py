# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Logging events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## Logging Started
##
class LoggingStarted(EventClass):
    name     = "Logging Started"
    category = "SECURITY"
    priority = "NORMAL"
    subject_template="Logging started: {{host}}:{{port}}"
    body_template="""Logging started: {{host}}:{{port}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        host=Var(required=True,repeat=False)
        port=Var(required=True,repeat=False)

##
## Logged Command
##
class LoggedCommand(EventClass):
    name     = "Logged Command"
    category = "SECURITY"
    priority = "NORMAL"
    subject_template="Command executed by {{user}}: {{command}}"
    body_template="""Command executed on equipment by user {{user}}
---
{{command}}
---"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        command=Var(required=True,repeat=False)
        user=Var(required=True,repeat=False)
