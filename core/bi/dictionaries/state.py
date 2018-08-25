# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# State BI dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, BooleanField


class State(Dictionary):
    class Meta:
        name = "state"
        layout = "flat"

    name = StringField()
    workflow = StringField()
    is_default = BooleanField()
    is_productive = BooleanField()
