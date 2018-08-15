# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.CPEStatus tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.sa.models.cpestatus import CPEStatus


class TestSaCPEStatus(BaseDocumentTest):
    model = CPEStatus
