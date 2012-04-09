# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IAuthenticationBackend interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IAuthenticationBackend(Interface):
    returns = InstanceOfParameter("User", required=False)
