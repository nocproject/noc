# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IReduceTask interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import InstanceOfParameter


class IReduceTask(BaseInterface):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    task = InstanceOfParameter("ReduceTask")
