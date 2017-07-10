# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetObjectsStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  IntParameter, BooleanParameter, NoneParameter)


class IGetObjectsStatus(BaseInterface):
    objects = ListOfParameter(element=IntParameter(), required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "object_id": IntParameter(),
        "status": BooleanParameter() | NoneParameter()  # Up/Down/Unknown
    }))
