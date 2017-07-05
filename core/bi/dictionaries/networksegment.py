# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NetworkSegment dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, ReferenceField


class NetworkSegment(Dictionary):
    class Meta:
        name = "networksegment"
        layout = "hashed"

    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value.id,
            "name": value.name,
            "parent": cls.lookup(value.parent) if value.parent else 0
        }
