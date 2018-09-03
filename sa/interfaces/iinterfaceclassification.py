# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IInterfaceClassification --
#     Interface classification pyRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import Parameter, NoneParameter, StringParameter


class IInterfaceClassification(BaseInterface):
    # Interface instance
    interface = Parameter()
    # Interface profile name
    returns = NoneParameter() | StringParameter()
