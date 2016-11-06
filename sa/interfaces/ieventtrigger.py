# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IEventTrigger interface
##----------------------------------------------------------------------
## Copyright (C) 2007-20101The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, InstanceOfParameter


class IEventTrigger(Interface):
    event = InstanceOfParameter("ActiveEvent")
