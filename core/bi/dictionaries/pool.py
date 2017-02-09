# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pool dictionary
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class Pool(Dictionary):
    class Meta:
        name = "pool"
        layout = "flat"

    name = StringField()

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value.id,
            "name": value.name
        }
