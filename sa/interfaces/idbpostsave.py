# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IDBPostSave
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IDBPostSave(Interface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
    created = BooleanParameter()
