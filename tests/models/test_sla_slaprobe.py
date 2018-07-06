# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sla.SLAProbe tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.sla.models.slaprobe import SLAProbe


class TestSlaSLAProbe(BaseDocumentTest):
    model = SLAProbe
