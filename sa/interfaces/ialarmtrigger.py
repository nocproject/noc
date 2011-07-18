# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IAlarmTrigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IAlarmTrigger(Interface):
    alarm = InstanceOfParameter("ActiveAlarm")
