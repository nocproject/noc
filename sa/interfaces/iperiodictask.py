# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IPeriodicTask interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import IntParameter, BooleanParameter


class IPeriodicTask(BaseInterface):
    timeout = IntParameter(default=0)
    returns = BooleanParameter(default=True)
