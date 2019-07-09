# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test Reboot model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from six.moves import zip_longest

# NOC modules
from noc.bi.models.reboots import Reboots

MODEL = Reboots

FIELDS = [
    ("date", "Date"),
    ("ts", "DateTime"),
    ("managed_object", "UInt64"),
    ("pool", "UInt64"),
    ("ip", "UInt32"),
    ("profile", "UInt64"),
    ("vendor", "UInt64"),
    ("platform", "UInt64"),
    ("version", "UInt64"),
    ("administrative_domain", "UInt64"),
    ("segment", "UInt64"),
    ("container", "UInt64"),
    ("x", "Float64"),
    ("y", "Float64"),
]

SQL = """CREATE TABLE IF NOT EXISTS reboots (
date Date,
ts DateTime,
managed_object UInt64,
pool UInt64,
ip UInt32,
profile UInt64,
vendor UInt64,
platform UInt64,
version UInt64,
administrative_domain UInt64,
segment UInt64,
container UInt64,
x Float64,
y Float64
) ENGINE = MergeTree(date, (ts, managed_object), 8192);"""


def test_fields_test():
    assert len(FIELDS) == len(MODEL._fields_order)


def test_sql():
    assert MODEL.get_create_sql() == SQL


@pytest.mark.parametrize("name,db_type", FIELDS)
def test_field_name(name, db_type):
    assert name in MODEL._fields


@pytest.mark.parametrize("name,db_type", FIELDS)
def test_field_db_type(name, db_type):
    assert MODEL._fields[name].get_db_type() == db_type


@pytest.mark.parametrize("order,fields", list(zip_longest(MODEL._fields_order, FIELDS)))
def test_field_order(order, fields):
    assert fields is not None
    name, db_type = fields
    assert order == name
