# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Workflow BI dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, BooleanField


class Workflow(Dictionary):
    class Meta:
        name = "workflow"
        layout = "flat"

    name = StringField()
    is_active = BooleanField()
