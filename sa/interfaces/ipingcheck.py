# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IPingCheck
# SAE service to check address availability
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import (ListOfParameter, DictParameter,
                   IPParameter, StringParameter, BooleanParameter)


class IPingCheck(BaseInterface):
    activator_name = StringParameter()
    addresses = ListOfParameter(IPParameter())
    returns = ListOfParameter(DictParameter(attrs={
        "ip": IPParameter(),
        "status": BooleanParameter()
    }))
