# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDictList interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, DictListParameter


class IGetDictList(Interface):
    returns = DictListParameter()
