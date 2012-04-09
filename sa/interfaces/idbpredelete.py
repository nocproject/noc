# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IDBPreDelete
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IDBPreDelete(Interface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
