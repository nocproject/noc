# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import VLANIDParameter, BooleanParameter


<<<<<<< HEAD
class IHasVlan(BaseInterface):
=======
class IHasVlan(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    vlan_id = VLANIDParameter()
    returns = BooleanParameter()
