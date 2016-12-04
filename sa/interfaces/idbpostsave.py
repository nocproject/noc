# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IDBPostSave
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, SubclassOfParameter, Parameter, BooleanParameter


class IDBPostSave(Interface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
    created = BooleanParameter()
