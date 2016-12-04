# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetList interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, ListParameter


class IGetList(Interface):
    returns = ListParameter()
