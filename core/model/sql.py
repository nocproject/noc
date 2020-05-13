# ---------------------------------------------------------------------
# Various database utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from django.db.models.query_utils import Q
from django.db.models.lookups import Lookup
from django.db.models.fields import Field


logger = logging.getLogger(__name__)


class SQLNode(Q):
    def __init__(self, sql):
        super().__init__(id__rawsql=sql)


def SQL(sql):
    """
    Q-style wrapper for SQL statement. Can be used in queryset
    together with Q
    """
    return SQLNode(sql)


@Field.register_lookup
class SQLLookup(Lookup):
    lookup_name = "rawsql"
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        return "(%s)" % self.rhs, []
