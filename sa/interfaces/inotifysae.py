# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# INotifySAE interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import StringParameter, BooleanParameter


class INotifySAE(BaseInterface):
    event = StringParameter()
    returns = BooleanParameter()
