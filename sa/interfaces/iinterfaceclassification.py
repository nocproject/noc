# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IInterfaceClassification --
#     Interface classification pyRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import Parameter, NoneParameter, StringParameter


class IInterfaceClassification(BaseInterface):
    # Interface instance
    interface = Parameter()
    # Interface profile name
    returns = NoneParameter() | StringParameter()
