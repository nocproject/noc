# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.correlation import *
from noc.fm.rules.classes.radius import *
##
## Radius Dead/Alive
##
class Radius_Dead_Alive_Rule(CorrelationRule):
    name="Radius Dead/Alive"
    description=""
    rule_type="Pair"
    action=CLOSE_EVENT
    same_object=False
    window=0
    classes=[RADIUSAlive,RADIUSDead]
    vars=["ip"]