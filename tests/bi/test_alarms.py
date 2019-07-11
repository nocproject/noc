# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test Alarms model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from six.moves import zip_longest

# NOC modules
from noc.bi.models.alarms import Alarms

MODEL = Alarms

FIELDS = [
    ("date", "Date"),
    ("ts", "DateTime"),
    ("close_ts", "DateTime"),
    ("duration", "Int32"),
    ("alarm_id", "String"),
    ("root", "String"),
    ("alarm_class", "UInt64"),
    ("severity", "Int32"),
    ("reopens", "Int32"),
    ("direct_services", "Int64"),
    ("direct_subscribers", "Int64"),
    ("total_objects", "Int64"),
    ("total_services", "Int64"),
    ("total_subscribers", "Int64"),
    ("escalation_ts", "DateTime"),
    ("escalation_tt", "String"),
    ("reboots", "Int16"),
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
    ("services.profile", "String"),
    ("services.summary", "UInt32"),
    ("subscribers.profile", "String"),
    ("subscribers.summary", "UInt32"),
    ("ack_user", "String"),
    ("ack_ts", "DateTime"),
]

SQL = """CREATE TABLE IF NOT EXISTS alarms (
date Date,
ts DateTime,
close_ts DateTime,
duration Int32,
alarm_id String,
root String,
alarm_class UInt64,
severity Int32,
reopens Int32,
direct_services Int64,
direct_subscribers Int64,
total_objects Int64,
total_services Int64,
total_subscribers Int64,
escalation_ts DateTime,
escalation_tt String,
reboots Int16,
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
y Float64,
`services.profile` Array(String),
`services.summary` Array(UInt32),
`subscribers.profile` Array(String),
`subscribers.summary` Array(UInt32),
ack_user String,
ack_ts DateTime
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
