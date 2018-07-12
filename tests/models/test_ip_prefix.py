# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip.Prefix tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.ip.models.prefix import Prefix


class TestTestIpPrefix(BaseModelTest):
    model = Prefix
