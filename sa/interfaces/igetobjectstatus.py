# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetObjectStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (ListOfParameter, DictParameter,
                   StringParameter, BooleanParameter)


class IGetObjectStatus(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "status": BooleanParameter()
    }))
    preview = "NOC.sa.managedobject.scripts.ShowObjectStatus"
