# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# kb.KBEntry tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.kb.models.kbentry import KBEntry


class TestTestKbKBEntry(BaseModelTest):
    model = KBEntry
