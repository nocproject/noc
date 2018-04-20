# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetHTTPGet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.interface.base import BaseInterface
from base import StringParameter


class IGetHTTPGet(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetHTTPGet
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from base import *


class IGetHTTPGet(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    url = StringParameter()
    returns = StringParameter()
