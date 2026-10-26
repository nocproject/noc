# ---------------------------------------------------------------------
# IGetList interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import ListParameter


class IGetList(BaseInterface):
    returns = ListParameter()
