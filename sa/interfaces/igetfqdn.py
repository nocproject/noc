# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetFQDN
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, StringParameter


class IGetFQDN(Interface):
    returns = StringParameter()
