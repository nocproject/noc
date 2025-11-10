# ----------------------------------------------------------------------
# Test Reboot model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.clickhouse.fields import BaseField
from noc.bi.models.reboots import Reboots

MODEL = Reboots

FIELDS = [
    ("date", "Date"),
    ("ts", "DateTime"),
    ("last", "DateTime"),
    ("managed_object", "UInt64"),
    ("pool", "UInt64"),
    ("ip", "UInt32"),
    ("profile", "UInt64"),
    ("object_profile", "UInt64"),
    ("vendor", "UInt64"),
    ("platform", "UInt64"),
    ("version", "UInt64"),
    ("administrative_domain", "UInt64"),
    ("segment", "UInt64"),
    ("container", "UInt64"),
    ("x", "Float64"),
    ("y", "Float64"),
]

SQL = """CREATE TABLE IF NOT EXISTS raw_reboots (
date Date,
ts DateTime,
last DateTime,
managed_object UInt64,
pool UInt64,
ip UInt32,
profile UInt64,
object_profile UInt64,
vendor UInt64,
platform UInt64,
version UInt64,
administrative_domain UInt64,
segment UInt64,
container UInt64,
x Float64,
y Float64
) ENGINE = MergeTree() PARTITION BY toYYYYMM(date) PRIMARY KEY (ts,managed_object) ORDER BY (ts,managed_object) SETTINGS index_granularity = 8192 ;"""


@pytest.mark.parametrize(("name", "db_type"), FIELDS)
def test_field_db_type(name, db_type):
    field_name, nested_name = BaseField.nested_path(name)
    assert MODEL._meta.fields[field_name].get_db_type(nested_name) == db_type


def test_iter_create_sql():
    assert list(MODEL.iter_create_sql()) == FIELDS


def test_get_create_fields_sql():
    expected = "\n".join(SQL.splitlines()[1:-1])
    assert MODEL.get_create_fields_sql() == expected


def test_get_create_sql():
    assert MODEL.get_create_sql() == SQL


def test_create_distributed_sql():
    assert MODEL.cget_create_distributed_sql()
