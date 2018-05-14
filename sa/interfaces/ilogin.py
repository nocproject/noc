# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import BooleanParameter, DictParameter, StringParameter


class ILogin(BaseInterface):
    returns = DictParameter(attrs={"result": BooleanParameter(),
                                   "message": StringParameter(default="")})

