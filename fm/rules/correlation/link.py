# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link-related correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.correlation import *
from noc.fm.rules.classes.link import *
##
## Link Up/Down
##
class Link_Up_Down(CorrelationRule):
    name="Link Up/Down"
    rule_type="Pair"
    same_object=True
    action=CLOSE_EVENT
    classes=[LinkUp,LinkDown]
    vars=["interface"]
