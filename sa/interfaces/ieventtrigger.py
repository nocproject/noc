# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IEventTrigger interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-20101The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface

from base import InstanceOfParameter


class IEventTrigger(BaseInterface):
    event = InstanceOfParameter("ActiveEvent")
