# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IDBPreSave
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import SubclassOfParameter, Parameter


class IDBPreSave(BaseInterface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
