# ----------------------------------------------------------------------
# Test core.clickhouse package
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict

# Third-party modules
import pytest

# NOC modules
from noc.core.clickhouse.model import Model, NestedModel
from noc.core.clickhouse.fields import StringField, Int8Field, NestedField, DateField
from noc.core.clickhouse.shard import ShardingFunction
from noc.config import CHClusterShard


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
    "data,expected",
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


@pytest.mark.parametrize(
    "topology,n,expected",
    [
        # Plain
        (
            [(1, 1)],
            4,
            {
                "chwriter-1-1": [
                    {"managed_object": 0, "name": "MO0000"},
                    {"managed_object": 1, "name": "MO0001"},
                    {"managed_object": 2, "name": "MO0002"},
                    {"managed_object": 3, "name": "MO0003"},
                ]
            },
        ),
        # 2 shards, 1 replica
        (
            [(1, 1), (1, 1)],
            4,
            {
                "chwriter-1-1": [
                    {"managed_object": 0, "name": "MO0000"},
                    {"managed_object": 2, "name": "MO0002"},
                ],
                "chwriter-2-1": [
                    {"managed_object": 1, "name": "MO0001"},
                    {"managed_object": 3, "name": "MO0003"},
                ],
            },
        ),
        # 3 shards, 1 replica
        (
            [(1, 1), (1, 1), (1, 1)],
            4,
            {
                "chwriter-1-1": [
                    {"managed_object": 0, "name": "MO0000"},
                    {"managed_object": 3, "name": "MO0003"},
                ],
                "chwriter-2-1": [{"managed_object": 1, "name": "MO0001"}],
                "chwriter-3-1": [{"managed_object": 2, "name": "MO0002"}],
            },
        ),
        # 2 shards, 1 and 2 replicas
        (
            [(1, 1), (2, 1)],
            4,
            {
                "chwriter-1-1": [
                    {"managed_object": 0, "name": "MO0000"},
                    {"managed_object": 2, "name": "MO0002"},
                ],
                "chwriter-2-1": [
                    {"managed_object": 1, "name": "MO0001"},
                    {"managed_object": 3, "name": "MO0003"},
                ],
                "chwriter-2-2": [
                    {"managed_object": 1, "name": "MO0001"},
                    {"managed_object": 3, "name": "MO0003"},
                ],
            },
        ),
    ],
)
def test_sharding_function(topology, n, expected):
    sf = ShardingFunction([CHClusterShard(*x) for x in topology])
    data = defaultdict(list)
    for i in range(n):
        record = {"managed_object": i, "name": "MO%04d" % i}
        for ch in sf("managed_object", record):
            data[ch] += [record]
    assert data == expected
