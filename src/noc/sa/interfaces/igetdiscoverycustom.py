# ---------------------------------------------------------------------
# IGetDiscoveryCustom
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import DictParameter, Parameter


class IGetDiscoveryCustom(BaseInterface):
    instance = Parameter()
    managed_object = Parameter()
    returns = DictParameter()
