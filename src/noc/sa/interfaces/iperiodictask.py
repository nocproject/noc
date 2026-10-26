# ---------------------------------------------------------------------
# IPeriodicTask interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import BooleanParameter, IntParameter


class IPeriodicTask(BaseInterface):
    timeout = IntParameter(default=0)
    returns = BooleanParameter(default=True)
