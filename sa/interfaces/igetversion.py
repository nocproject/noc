# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import DictParameter, StringParameter


class IGetVersion(BaseInterface):
    returns = DictParameter(attrs={
        "vendor": StringParameter(),
        "platform": StringParameter(),
        "version": StringParameter(),
        "attributes": DictParameter(required=False)
    })
