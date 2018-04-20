# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IConfigFilter
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import InstanceOfParameter, StringParameter


class IConfigFilter(BaseInterface):
=======
##----------------------------------------------------------------------
## IConfigFilter
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IConfigFilter(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    managed_object = InstanceOfParameter("ManagedObject")
    config = StringParameter()
    returns = StringParameter()
