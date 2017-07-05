# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Container dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, ReferenceField


class Container(Dictionary):
    class Meta:
        name = "container"
        layout = "hashed"

    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value.id,
            "name": value.name,
            "parent": cls.lookup(value.get_by_id(value.container)) if value.container else 0
        }
