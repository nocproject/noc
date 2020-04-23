# ---------------------------------------------------------------------
# IGetSNMPGet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import OIDParameter, StringParameter, NoneParameter


class IGetSNMPGet(BaseInterface):
    oid = OIDParameter()
    community_suffix = StringParameter(required=False)
    returns = NoneParameter() | StringParameter()
