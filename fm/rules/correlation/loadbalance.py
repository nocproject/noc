# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Loadbalancer correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.correlation import *
from noc.fm.rules.classes.loadbalance import *
##
## LB Pool Member Up/Down
##
class LB_Pool_Member_Up_Down_Rule(CorrelationRule):
    name="LB Pool Member Up/Down"
    description=""
    rule_type="Pair"
    action=CLOSE_EVENT
    same_object=True
    window=0
    classes=[LBPoolMemberDown,LBPoolMemberUp]
    vars=["port","node"]
