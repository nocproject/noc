# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetVerson interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictParameter, StringParameter


class IGetVersion(BaseInterface):
    returns = DictParameter(attrs={
        "vendor": StringParameter(),
        "platform": StringParameter(),
        "version": StringParameter(),
        "image": StringParameter(required=False),
        "attributes": DictParameter(required=False)
    })
