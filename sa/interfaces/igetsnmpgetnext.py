# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetSNMPGetNext
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from base import *


class IGetSNMPGetNext(Interface):
    oid = OIDParameter()
    community_suffix = StringParameter(required=False)
    bulk = BooleanParameter(default=True)
    min_index = IntParameter(required=False)
    max_index = IntParameter(required=False)
    
    returns = (NoneParameter() |
               ListOfParameter(element=[OIDParameter(), StringParameter()]))
    template = "interfaces/igetsnmpgetnext.html"
