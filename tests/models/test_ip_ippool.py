# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip.IPPool tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.ip.models.ippool import IPPool


class TestTestIpIPPool(BaseModelTest):
    model = IPPool
