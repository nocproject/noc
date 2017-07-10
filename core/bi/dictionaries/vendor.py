# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vendor dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class Vendor(Dictionary):
    class Meta:
        name = "vendor"
        layout = "flat"

    name = StringField()

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value,
            "name": value
        }
