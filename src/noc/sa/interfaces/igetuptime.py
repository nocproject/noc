# ---------------------------------------------------------------------
# IGetUptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import FloatParameter, NoneParameter


class IGetUptime(BaseInterface):
    """
    System uptime in seconds
    """

    returns = NoneParameter() | FloatParameter()
