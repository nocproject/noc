# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## IEventTrigger interface
##----------------------------------------------------------------------
## Copyright (C) 2007-20101The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IEventTrigger(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    event = InstanceOfParameter("ActiveEvent")
