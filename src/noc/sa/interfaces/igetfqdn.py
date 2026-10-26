# ---------------------------------------------------------------------
# IGetFQDN
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import StringParameter


class IGetFQDN(BaseInterface):
    returns = StringParameter()
