# ----------------------------------------------------------------------
# BaseMigration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.mongo.connection import get_db
from .db import db


class BaseMigration(object):
    depends_on = []
    db = db

    def __init__(self):
        # @todo: set_comprehensions
        self.dependencies = {f"{x[0]}.{x[1]}" for x in self.depends_on}

    def __str__(self):
        return self.get_name()

    def add_dependency(self, name):
        self.dependencies.add(name)

    def is_resolved(self, dependencies):
        """
        Check if all dependencies is resolved
        :param dependencies: Set of seen dependencies
        :return:
        """
        return not bool(self.dependencies - dependencies)

    @classmethod
    def get_name(cls):
        parts = cls.__module__.split(".")
        return "%s.%s" % (parts[1], parts[3])

    @property
    def mongo_db(self):
        return get_db()

    def migrate(self):
        """
        Actual migration code
        :return:
        """
