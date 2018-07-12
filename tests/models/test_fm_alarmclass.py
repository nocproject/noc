# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.AlarmClass tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.fm.models.alarmclass import AlarmClass


class TestFmAlarmClass(BaseDocumentTest):
    model = AlarmClass
