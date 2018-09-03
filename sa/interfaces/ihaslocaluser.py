# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IHasLocalUser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import StringParameter, BooleanParameter


class IHasLocalUser(BaseInterface):
    username = StringParameter()
    returns = BooleanParameter()
