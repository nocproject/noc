# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip.Address tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.ip.models.address import Address


class TestTestIpAddress(BaseModelTest):
    model = Address
