# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.VCDomain tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.vc.models.vcdomain import VCDomain


class TestTestVcVCDomain(BaseModelTest):
    model = VCDomain
