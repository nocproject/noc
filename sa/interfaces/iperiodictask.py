# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IPeriodicTask interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import IntParameter, BooleanParameter


class IPeriodicTask(BaseInterface):
=======
##----------------------------------------------------------------------
## IPeriodicTask interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IPeriodicTask(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    timeout = IntParameter(default=0)
    returns = BooleanParameter(default=True)
