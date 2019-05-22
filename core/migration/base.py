# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseMigration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import six
# NOC modules
from noc.lib.nosql import get_db
from .db import db


@six.python_2_unicode_compatible
class BaseMigration(object):
    depends_on = []
    db = db

    def __str__(self):
        return self.get_name()

    @classmethod
    def get_name(cls):
        parts = cls.__module__.split(".")
        return u"%s.%s" % (parts[1], parts[3])

    @property
    def mongo_db(self):
        return get_db()

    def migrate(self):
        """
        Actual migration code
        :return:
        """
        pass

    def forwards(self):
        """
        South-compatible method
        :return:
        """
        self.migrate()

    def backwards(self):
        """
        South-compatible method
        :return:
        """
        pass
