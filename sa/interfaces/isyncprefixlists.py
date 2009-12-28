# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ISyncPrefixLists interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class ISyncPrefixLists(Interface):
    changed_prefix_lists=ListOfParameter(element=DictParameter(attrs={"name":StringParameter(),
                                                                      "prefix_list":ListOfParameter(element=IPv4PrefixParameter()),
                                                                      "strict": BooleanParameter()}))
    returns=ListOfParameter(element=DictParameter(attrs={"name":StringParameter(),"status":BooleanParameter()}))
