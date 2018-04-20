# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# INotifySAE interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import StringParameter, BooleanParameter


class INotifySAE(BaseInterface):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    event = StringParameter()
    returns = BooleanParameter()
