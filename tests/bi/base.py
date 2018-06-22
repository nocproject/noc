# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BI testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseBIModelTest(object):
    # BI model
    model = None
    # List of (name, db_type)
    FIELDS = []
    CREATE = ""

    def test_field_sequence(self):
        for fn, (rn, rt) in zip(self.model._fields_order, self.FIELDS):
            assert fn == rn
            assert self.model._fields[fn].get_db_type() == rt
            assert self.model.get_create_sql() == self.CREATE


class BaseDictionaryTest(object):
    # BI dictionary
    model = None
    # List of (name, db_type)
    FIELDS = []

    def test_field_sequence(self):
        for fn, (rn, rt) in zip(self.model._fields_order, self.FIELDS):
            assert fn == rn
            assert self.model._fields[fn].get_db_type() == rt
