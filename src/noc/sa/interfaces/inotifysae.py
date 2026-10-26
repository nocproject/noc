# ---------------------------------------------------------------------
# INotifySAE interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import BooleanParameter, StringParameter


class INotifySAE(BaseInterface):
    event = StringParameter()
    returns = BooleanParameter()
