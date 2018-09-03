# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IAuthenticationBackend interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.interface.base import BaseInterface
from .base import InstanceOfParameter


class IAuthenticationBackend(BaseInterface):
    returns = InstanceOfParameter("User", required=False)
