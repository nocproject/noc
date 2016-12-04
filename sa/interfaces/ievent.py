# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IEvent interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, InstanceOfParameter


class IEvent(Interface):
    event = InstanceOfParameter("Event")
