# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import DictParameter, ListOfParameter, StringParameter


class IGetConfig(BaseInterface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "config": StringParameter()
    })) | StringParameter()
    preview = "NOC.sa.managedobject.scripts.TextPreview"
