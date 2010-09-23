# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPingCheck
## SAE service to check address availability
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IPingCheck(Interface):
    activator_name=StringParameter()
    addresses=ListOfParameter(IPParameter())
    returns=ListOfParameter(DictParameter(attrs={
        "ip"     : IPParameter(),
        "status" : BooleanParameter()
    }))
