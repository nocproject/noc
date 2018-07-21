# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sla.SLAProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.sla.models.slaprofile import SLAProfile


class TestSlaSLAProfile(BaseDocumentTest):
    model = SLAProfile
