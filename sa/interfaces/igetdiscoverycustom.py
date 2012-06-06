# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDiscoveryCustom
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import *


class IGetDiscoveryCustom(Interface):
    instance = Parameter()
    managed_object = Parameter()
    returns = DictParameter()
