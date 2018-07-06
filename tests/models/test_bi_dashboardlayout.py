# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# bi.DashboardLayout tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.bi.models.dashboardlayout import DashboardLayout


class TestBiDashboardLayout(BaseDocumentTest):
    model = DashboardLayout
