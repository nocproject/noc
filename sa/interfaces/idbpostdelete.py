# -*- coding: utf-8 -*-
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
    model = SubclassOfParameter("Model")
    instance = Parameter()
