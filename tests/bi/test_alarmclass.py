# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AlarmClass dictionary test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.bi.dictionaries.alarmclass import AlarmClass
from .base import BaseDictionaryTest


class TestAlarmClass(BaseDictionaryTest):
    model = AlarmClass
    FIELDS = [
        ("name", "String")
    ]
