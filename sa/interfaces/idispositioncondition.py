# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IDispositionCondition
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import InstanceOfParameter, StringParameter, BooleanParameter


class IDispositionCondition(BaseInterface):
=======
##----------------------------------------------------------------------
## IDispositionCondition
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IDispositionCondition(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rule_name = StringParameter()
    event = InstanceOfParameter("ActiveEvent")
    returns = BooleanParameter()
