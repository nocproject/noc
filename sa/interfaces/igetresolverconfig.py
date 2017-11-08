# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetResolverConfig interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface

from base import (DictParameter, ListOfParameter,
                  IPParameter, StringParameter, StringListParameter)


class IGetResolverConfig(BaseInterface):
    returns = DictParameter(attrs={
        "domain": StringParameter(required=False),
        "search": StringListParameter(required=False),
        "nameservers": ListOfParameter(element=IPParameter(), required=False)
    })
