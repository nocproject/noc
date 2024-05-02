# ---------------------------------------------------------------------
# IGetSNMPAvailability
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import BooleanParameter


class IGetSNMPAvailability(BaseInterface):
    returns = BooleanParameter()
