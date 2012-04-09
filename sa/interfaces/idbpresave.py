# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IDBPreSave
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IDBPreSave(Interface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
