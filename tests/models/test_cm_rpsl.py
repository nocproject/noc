# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.RPSL tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.cm.models.rpsl import RPSL


class TestTestCmRPSL(BaseModelTest):
    model = RPSL
