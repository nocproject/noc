# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetHTTPGet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.interface.base import BaseInterface

from base import StringParameter


class IGetHTTPGet(BaseInterface):
    url = StringParameter()
    returns = StringParameter()
