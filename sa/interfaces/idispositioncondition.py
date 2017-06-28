# -*- coding: utf-8 -*-
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
    rule_name = StringParameter()
    event = InstanceOfParameter("ActiveEvent")
    returns = BooleanParameter()
