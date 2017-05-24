# -*- coding: utf-8 -*-
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
    model = SubclassOfParameter("Model")
    instance = Parameter()
