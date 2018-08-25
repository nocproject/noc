# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.SlowOp tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.main.models.slowop import SlowOp


class TestMainSlowOp(BaseDocumentTest):
    model = SlowOp
