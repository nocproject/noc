# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetLicense
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, DictParameter


class IGetLicense(Interface):
    returns = DictParameter()
