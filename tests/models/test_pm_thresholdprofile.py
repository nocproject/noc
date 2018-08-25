# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pm.ThresholdProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.pm.models.thresholdprofile import ThresholdProfile


class TestPmThresholdProfile(BaseDocumentTest):
    model = ThresholdProfile
