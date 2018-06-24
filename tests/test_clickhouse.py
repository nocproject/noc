# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test core.clickhouse package
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
from noc.core.clickhouse.model import Model, NestedModel
from noc.core.clickhouse.fields import (
    StringField, Int8Field, NestedField, DateField, DateTimeField
)


def test_nested():
    class Pair(NestedModel):
        index = Int8Field()
        text = StringField()

    class MyModel(Model):
        class Meta(object):
            db_table = "mymodel"

        date = DateField()
        text = StringField()
        pairs = NestedField(Pair)

    # Check field order and fingerprint
    assert MyModel.get_fingerprint() == "mymodel|date|text|pairs.index|pairs.text"
    # Check TSV conversion
    today = datetime.date.today()
    tsv = MyModel.to_tsv(
        date=today,
        text="Test",
        pairs=[
            {
                "index": 1,
                "text": "First"
            },
            {
                "index": 2,
                "text": "Second"
            }
        ]
    )
    valid_tsv = "%s\tTest\t[1,2]\t['First','Second']\n" % today.isoformat()
    assert tsv == valid_tsv
