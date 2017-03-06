# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IAlarmTrigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.interface.base import BaseInterface
from base import InstanceOfParameter


class IAlarmTrigger(BaseInterface):
    alarm = InstanceOfParameter("ActiveAlarm")
