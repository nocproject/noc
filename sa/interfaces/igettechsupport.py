# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  StringParameter)


class IGetTechSupport(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "section": StringParameter()
    })) | StringParameter()
    preview = "NOC.sa.managedobject.scripts.TextPreview"
