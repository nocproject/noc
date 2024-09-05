# ---------------------------------------------------------------------
# ISetParam Interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import BooleanParameter, StringParameter, FloatParameter, IntParameter


class ISetParam(BaseInterface):
    # Chassis id
    chassis = IntParameter()
    # Card id
    card = IntParameter()
    # Param name
    name = StringParameter()
    # Param value
    value = IntParameter() | FloatParameter() | StringParameter()
    returns = BooleanParameter()
