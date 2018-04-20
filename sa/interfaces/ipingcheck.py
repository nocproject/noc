# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IPingCheck
# SAE service to check address availability
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  IPParameter, StringParameter, BooleanParameter)


class IPingCheck(BaseInterface):
=======
##----------------------------------------------------------------------
## IPingCheck
## SAE service to check address availability
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IPingCheck(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    activator_name = StringParameter()
    addresses = ListOfParameter(IPParameter())
    returns = ListOfParameter(DictParameter(attrs={
        "ip": IPParameter(),
        "status": BooleanParameter()
    }))
