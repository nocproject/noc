# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## INotifySAE interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class INotifySAE(Interface):
    event = StringParameter()
    returns = BooleanParameter()
