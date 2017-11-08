# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.interface.base import BaseInterface

from base import BooleanParameter


class ILogin(BaseInterface):
    returns = BooleanParameter()
