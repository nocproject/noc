# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IReduceTask interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IReduceTask(Interface):
    task = InstanceOfParameter("ReduceTask")
