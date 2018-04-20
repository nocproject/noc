# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetUptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import FloatParameter, NoneParameter


class IGetUptime(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetUptime
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetUptime(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    System uptime in seconds
    """
    returns = NoneParameter() | FloatParameter()
