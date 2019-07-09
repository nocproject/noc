# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AlarmClass dictionary test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from six.moves import zip_longest

# NOC modules
from noc.core.bi.dictionaries.alarmclass import AlarmClass


MODEL = AlarmClass
FIELDS = [("name", "String")]


def test_fields_test():
    assert len(FIELDS) == len(MODEL._fields_order)


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
