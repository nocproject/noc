# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base testing classes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import connection
import pytest


@pytest.mark.usefixtures("database")
class BaseModelTest(object):
    model = None  # Must be overriden

    def get_cursor(self):
        return connection.cursor()

    def test_database_table(self):
        """
        Check database table is created during migration
        :return:
        """
        assert self.model._meta.db_table
        c = self.get_cursor()
        c.execute(
            "SELECT COUNT(*) FROM pg_class WHERE relname=%s",
            [self.model._meta.db_table]
        )
        return c.fetchall()[0][0] == 1

    def test_uncode(self):
        for o in self.model.objects.all():
            assert unicode(o)


@pytest.mark.usefixtures("database")
class BaseDocumentTest(object):
    model = None  # Must be overriden

    def get_collection(self):
        return self.model._get_collection()

    def test_uncode(self):
        for o in self.model.objects.all():
            assert unicode(o)
