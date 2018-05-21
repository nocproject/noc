# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Interface Profile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class ServiceProfile(Dictionary):
    class Meta:
        name = "serviceprofile"
        layout = "flat"

    name = StringField()
    desription = StringField()
    glyph = StringField()
