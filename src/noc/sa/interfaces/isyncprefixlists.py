# ---------------------------------------------------------------------
# ISyncPrefixLists interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC Modules
# NOC modules
from noc.core.interface.base import BaseInterface

from .base import (
    BooleanParameter,
    DictParameter,
    IPv4PrefixParameter,
    ListOfParameter,
    StringParameter,
)


class ISyncPrefixLists(BaseInterface):
    changed_prefix_lists = ListOfParameter(
        element=DictParameter(
            attrs={
                "name": StringParameter(),
                "prefix_list": ListOfParameter(element=IPv4PrefixParameter()),
                "strict": BooleanParameter(),
            }
        )
    )
    returns = ListOfParameter(
        element=DictParameter(attrs={"name": StringParameter(), "status": BooleanParameter()})
    )
