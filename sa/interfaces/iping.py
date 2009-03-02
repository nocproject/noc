# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IPing(Interface):
    address=IPParameter()
    returns=StringParameter(DictParameter(attrs={
        "success":IntParameter(),
        "count":IntParameter(),
    }))
