# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetCapabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from base import (Interface, DictParameter)


class IGetCapabilities(Interface):
    returns = DictParameter()
