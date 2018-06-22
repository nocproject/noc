# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test Reboot model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.bi.models.reboots import Reboots
from .base import BaseBIModelTest


class TestReboots(BaseBIModelTest):
    model = Reboots
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
    CREATE = """CREATE TABLE IF NOT EXISTS reboots (
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
