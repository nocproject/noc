# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetList interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import ListParameter


class IGetList(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetList interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetList(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListParameter()
