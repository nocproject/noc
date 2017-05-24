# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetDictList interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import DictListParameter


class IGetDictList(BaseInterface):
    returns = DictListParameter()
