# ---------------------------------------------------------------------
# IGetSNMPGet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import NoneParameter, OIDParameter, StringParameter


class IGetSNMPGet(BaseInterface):
    oid = OIDParameter()
    community_suffix = StringParameter(required=False)
    returns = NoneParameter() | StringParameter()
