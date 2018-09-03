# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (VLANIDParameter, StringParameter,
                   StringListParameter, BooleanParameter)


class IAddVlan(BaseInterface):
    vlan_id = VLANIDParameter()
    name = StringParameter()
    tagged_ports = StringListParameter(default=[])
    returns = BooleanParameter()
