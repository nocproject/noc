# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AdministrativeDomain dictionary
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, ReferenceField


class AdministrativeDomain(Dictionary):
    class Meta:
        name = "administrativedomain"
        layout = "flat"

    name = StringField()
    parent = ReferenceField("self")

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value.id,
            "name": value.name,
            "parent": cls.lookup(value.parent) if value.parent else 0
        }
