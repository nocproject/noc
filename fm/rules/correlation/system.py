# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.correlation import *
from noc.fm.rules.classes.system import *
##
## Object Reachable/Unreachable
##
class Object_Reachable_Unreachable_Rule(CorrelationRule):
    name="Object Reachable/Unreachable"
    description=""
    rule_type="Pair"
    action=CLOSE_EVENT
    same_object=True
    window=0
    classes=[ObjectReachable,ObjectUnreachable]
    vars=[]