# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IAlarmEnrichment
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IAlarmEnrichment(Interface):
    alarm = InstanceOfParameter("ActiveAlarm")
    returns = DictParameter()
