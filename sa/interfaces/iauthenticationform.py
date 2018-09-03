# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IAuthenticationForn interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import ListOfParameter, DictParameter, StringParameter


class IAuthenticationForm(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "xtype": StringParameter(),
        "name": StringParameter()
    }))
