# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IHasLocalUser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import StringParameter, BooleanParameter


class IHasLocalUser(BaseInterface):
=======
##----------------------------------------------------------------------
## IHasLocalUser
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IHasLocalUser(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    username = StringParameter()
    returns = BooleanParameter()
