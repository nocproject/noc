# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPeriodicTask interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IPeriodicTask(Interface):
    timeout = IntParameter(default=0)
    returns = BooleanParameter(default=True)
