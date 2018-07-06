# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.EventTrigger tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.fm.models.eventtrigger import EventTrigger


class TestTestFmEventTrigger(BaseModelTest):
    model = EventTrigger
