# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test Alarms model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.bi.models.alarms import Alarms
from .base import BaseBIModelTest


class TestAlarms(BaseBIModelTest):
    model = Alarms
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
        ("subscribers.summary", "UInt32")
    ]
    CREATE = """CREATE TABLE IF NOT EXISTS alarms (
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
`services.profile` String,
`services.summary` UInt32,
`subscribers.profile` String,
`subscribers.summary` UInt32
) ENGINE = MergeTree(date, (ts, managed_object), 8192);"""