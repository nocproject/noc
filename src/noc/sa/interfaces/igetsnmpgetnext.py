# ---------------------------------------------------------------------
# IGetSNMPGetNext
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import (
    BooleanParameter,
    IntParameter,
    ListOfParameter,
    NoneParameter,
    OIDParameter,
    StringParameter,
)


class IGetSNMPGetNext(BaseInterface):
    oid = OIDParameter()
    community_suffix = StringParameter(required=False)
    bulk = BooleanParameter(default=True)
    min_index = IntParameter(required=False)
    max_index = IntParameter(required=False)

    returns = NoneParameter() | ListOfParameter(element=[OIDParameter(), StringParameter()])
