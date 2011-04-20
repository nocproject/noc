# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetLicense
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetLicense(Interface):
    returns = DictParameter()
    template = "interfaces/igetlicense.html"
