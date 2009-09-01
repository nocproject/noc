# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IHasLocalUser
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IHasLocalUser(Interface):
    username=StringParameter()
    returns=BooleanParameter()
