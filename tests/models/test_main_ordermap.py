# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.OrderMap tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.main.models.ordermap import OrderMap


class TestTestMainOrderMap(BaseModelTest):
    model = OrderMap
