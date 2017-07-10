# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class ManagedObject(Dictionary):
    class Meta:
        name = "managedobject"
        layout = "hashed"

    name = StringField()

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value.id,
            "name": value.name
        }
