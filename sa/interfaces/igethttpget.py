# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetHTTPGet
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from base import *


class IGetHTTPGet(Interface):
    url = StringParameter()
    returns = StringParameter()
