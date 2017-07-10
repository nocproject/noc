# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetLicense
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import DictParameter


class IGetLicense(BaseInterface):
    returns = DictParameter()
