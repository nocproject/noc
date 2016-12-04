# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IInterfaceClassification --
##     Interface classification pyRule
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Interface, Parameter, NoneParameter, StringParameter


class IInterfaceClassification(Interface):
    # Interface instance
    interface = Parameter()
    # Interface profile name
    returns = NoneParameter() | StringParameter()
