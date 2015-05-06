# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetSNMPGet
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from base import *

class IGetSNMPGet(Interface):
    oid = OIDParameter()
    community_suffix = StringParameter(required=False)
    returns = NoneParameter() | StringParameter()
