# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Interface Description dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class InterfaceDescription(Dictionary):
    class Meta:
        name = "interfacedescription"
        layout = "flat"

    description = StringField()

