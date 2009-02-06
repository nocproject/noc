# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetVersion(Interface):
    returns=DictParameter(attrs={
                                "vendor"  : StringParameter(),
                                "platform": StringParameter(),
                                "version" : StringParameter(),
                                "image"   : StringParameter(required=False)
                                })
