# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alarm Class dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class AlarmClass(Dictionary):
    class Meta:
        name = "alarmclass"
        layout = "flat"

    name = StringField()
