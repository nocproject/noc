# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## platform dictionary
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class Platform(Dictionary):
    class Meta:
        name = "platform"
        layout = "flat"

    name = StringField()

    @classmethod
    def get_record(cls, value):
        return {
            "_id": value,
            "name": value
        }
