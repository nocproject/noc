# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IInterfaceClassification --
#     Interface classification pyRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import Parameter, NoneParameter, StringParameter


class IInterfaceClassification(BaseInterface):
=======
##----------------------------------------------------------------------
## IInterfaceClassification --
##     Interface classification pyRule
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IInterfaceClassification(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    # Interface instance
    interface = Parameter()
    # Interface profile name
    returns = NoneParameter() | StringParameter()
