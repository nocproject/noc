# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IDispositionCondition
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IDispositionCondition(Interface):
    rule_name = StringParameter()
    event = InstanceOfParameter("ActiveEvent")
    returns = BooleanParameter()
