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
from noc.core.clickhouse.fields import DateField, Int8Field, NestedField, StringField
from noc.core.clickhouse.info import TableInfo
from noc.core.clickhouse.model import Model, NestedModel


class Pair(NestedModel):
    index = Int8Field()
    text = StringField()


class MyModel(Model):
    class Meta:
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
def test_to_json(data, expected) -> None:
    assert MyModel.to_json(**data) == expected


@pytest.mark.xfail
def test_mymodel_to_python() -> None:
    # Check TSV conversion
    today = datetime.date.today()
    ch_data = MyModel.to_python([today.isoformat(), "Test", "1:'First',2:'Second'"])
    valid_data = {
        "date": today,
        "text": "Test",
        "pairs": [{"index": 1, "text": "First"}, {"index": 2, "text": "Second"}],
    }
    assert ch_data == valid_data


PARSE_SQL1 = "CREATE TABLE noc.raw_syslog (`date` Date, `ts` DateTime, `managed_object` UInt64, `facility` UInt8, `severity` UInt8, `message` String) ENGINE = MergeTree PARTITION BY toYYYYMM(date) PRIMARY KEY (managed_object, ts) ORDER BY (managed_object, ts) TTL ts + toIntervalDay(365) SETTINGS index_granularity = 8192"
PARSE_SQL2 = "CREATE TABLE noc.raw_syslog (`date` Date, `ts` DateTime, `managed_object` UInt64, `facility` UInt8, `severity` UInt8, `message` String) ENGINE = MergeTree PARTITION BY toYYYYMM(date) PRIMARY KEY (managed_object, ts) ORDER BY (managed_object, ts) SETTINGS index_granularity = 8192"


@pytest.mark.parametrize(
    ("sql", "info"),
    [
        (PARSE_SQL1, TableInfo(name="raw_syslog", table_ttl=365 * 24 * 3600)),
        (PARSE_SQL2, TableInfo(name="raw_syslog")),
    ],
)
def test_tableinfo_from_sql(sql: str, info: TableInfo) -> None:
    r = TableInfo.from_sql(sql)
    assert r == info


@pytest.mark.parametrize("sql", ["REATE TABLE", "CREATE TABLE xxx (zzzz"])
def test_tableinfo_from_sql_error(sql: str) -> None:
    with pytest.raises(ValueError):
        TableInfo.from_sql(sql)
