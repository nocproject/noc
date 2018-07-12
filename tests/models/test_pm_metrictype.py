# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pm.MetricType tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.pm.models.metrictype import MetricType


class TestPmMetricType(BaseDocumentTest):
    model = MetricType
