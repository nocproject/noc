# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test core.clickhouse package
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest

# NOC modules
from noc.core.clickhouse.model import Model, NestedModel
from noc.core.clickhouse.fields import StringField, Int8Field, NestedField, DateField


class Pair(NestedModel):
    index = Int8Field()
    text = StringField()


class MyModel(Model):
    class Meta(object):
        db_table = "mymodel"

    date = DateField()
    text = StringField()
    pairs = NestedField(Pair)


def test_mymodel_fingerprint():
    # Check field order and fingerprint
    assert MyModel.get_fingerprint() == "mymodel|date|text|pairs.index|pairs.text"


def test_mymodel_to_tsv():
    # Check TSV conversion
    today = datetime.date.today()
    tsv = MyModel.to_tsv(
        date=today,
        text="Test",
        pairs=[{"index": 1, "text": "First"}, {"index": 2, "text": "Second"}],
    )
    valid_tsv = "%s\tTest\t[1,2]\t['First','Second']\n" % today.isoformat()
    assert tsv == valid_tsv


@pytest.mark.xfail
def test_mymodel_to_python():
    # Check TSV conversion
    today = datetime.date.today()
    ch_data = MyModel.to_python([today.isoformat(), "Test", "1:'First',2:'Second'"])
    valid_data = {
        "date": today,
        "text": "Test",
        "pairs": [{"index": 1, "text": "First"}, {"index": 2, "text": "Second"}],
    }
    assert ch_data == valid_data
