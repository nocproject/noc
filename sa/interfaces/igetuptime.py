# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetUptime
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetUptime(Interface):
    returns = NoneParameter() | IntParameter()
