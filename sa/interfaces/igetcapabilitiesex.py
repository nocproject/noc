# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetCapabilitiesExt
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import (Interface, DictParameter)


class IGetCapabilitiesEx(Interface):
    caps = DictParameter()
    returns = DictParameter()
