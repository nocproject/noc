# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.VCFilter tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.vc.models.vcfilter import VCFilter


class TestTestVcVCFilter(BaseModelTest):
    model = VCFilter
