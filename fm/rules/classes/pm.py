# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performance Management Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## PM OK
##
class PMOK(EventClass):
    name     = "PM OK"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="{{probe_name}}@{{service}}"
    body_template="""Probe Name: {{probe_name}}
Probe Type: {{probe_type}}
Service: {{service}}
Result: OK"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        probe_name=Var(required=True,repeat=False)
        probe_type=Var(required=True,repeat=False)
        service=Var(required=True,repeat=False)
        result=Var(required=True,repeat=False)

##
## PM OK
##
class PMOK(EventClass):
    name     = "PM OK"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="{{probe_name}}@{{service}}: {{message}}"
    body_template="""Probe Name: {{probe_name}}
Probe Type: {{probe_type}}
Service: {{service}}
Result: OK"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        probe_name=Var(required=True,repeat=False)
        probe_type=Var(required=True,repeat=False)
        service=Var(required=True,repeat=False)
        message=Var(required=True,repeat=False)
##
## PM OK
##
class PMWARN(EventClass):
    name     = "PM WARN"
    category = "NETWORK"
    priority = "WARNING"
    subject_template="{{probe_name}}@{{service}}: {{message}}"
    body_template="""Probe Name: {{probe_name}}
Probe Type: {{probe_type}}
Service: {{service}}
Result: WARNING
Message: {{message}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        probe_name=Var(required=True,repeat=False)
        probe_type=Var(required=True,repeat=False)
        service=Var(required=True,repeat=False)
        message=Var(required=True,repeat=False)
##
## PM FAIL
##
class PMFAIL(EventClass):
    name     = "PM FAIL"
    category = "NETWORK"
    priority = "CRITICAL"
    subject_template="{{probe_name}}@{{service}}: {{message}}"
    body_template="""Probe Name: {{probe_name}}
Probe Type: {{probe_type}}
Service: {{service}}
Result: FAIL
Message: {{message}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        probe_name=Var(required=True,repeat=False)
        probe_type=Var(required=True,repeat=False)
        service=Var(required=True,repeat=False)
        message=Var(required=True,repeat=False)
