# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pm.MetricScope tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.pm.models.metricscope import MetricScope


class TestPmMetricScope(BaseDocumentTest):
    model = MetricScope
