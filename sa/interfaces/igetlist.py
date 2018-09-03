# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetList interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import ListParameter


class IGetList(BaseInterface):
    returns = ListParameter()
