# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load Balancer Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## LB Pool Member Down
##
class LBPoolMemberDown(EventClass):
    name     = "LB Pool Member Down"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="Node is down: {{node}}:{{port}}"
    body_template="""Pool member {{node}}:{{port}} marked as DOWN"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        node=Var(required=True,repeat=False)
        port=Var(required=True,repeat=False)
##
## LB Pool Member Up
##
class LBPoolMemberUp(EventClass):
    name     = "LB Pool Member Up"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="Node is up: {{node}}:{{port}}"
    body_template="""Pool member {{node}}:{{port}} is up again"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        node=Var(required=True,repeat=False)
        port=Var(required=True,repeat=False)