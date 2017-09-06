# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# platform dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class Platform(Dictionary):
    class Meta:
        name = "platform"
        layout = "flat"

    # Platform name
    name = StringField()
    # Vendor name
    vendor = StringField()
    # <vendor> <platdorm>
    full_name = StringField()
