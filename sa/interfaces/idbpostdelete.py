# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IDBPostDelete
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import SubclassOfParameter, Parameter


class IDBPostDelete(BaseInterface):
=======
##----------------------------------------------------------------------
## IDBPostDelete
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IDBPostDelete(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    model = SubclassOfParameter("Model")
    instance = Parameter()
