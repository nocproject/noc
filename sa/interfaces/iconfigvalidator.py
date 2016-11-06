# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IConfigValidator
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, InstanceOfParameter, StringParameter, StringListParameter


class IConfigValidator(Interface):
    managed_object = InstanceOfParameter("ManagedObject")
    config = StringParameter()
    returns = StringListParameter()
