# ----------------------------------------------------------------------
# Test core.clickhouse package
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
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


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "date": datetime.date(year=2019, month=9, day=26),
                "text": "Test",
                "pairs": [{"index": 1, "text": "First"}, {"index": "2", "text": "Second"}],
            },
            {
                "date": "2019-09-26",
                "pairs.index": [1, 2],
                "pairs.text": ["First", "Second"],
                "text": "Test",
            },
        )
    ],
)
def test_to_json(data, expected):
    assert MyModel.to_json(**data) == expected


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
