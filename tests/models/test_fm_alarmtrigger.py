# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.AlarmTrigger tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.fm.models.alarmtrigger import AlarmTrigger


class TestTestFmAlarmTrigger(BaseModelTest):
    model = AlarmTrigger
