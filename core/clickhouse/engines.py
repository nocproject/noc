# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clickhouse engines
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

DEFAULT_MERGE_TREE_GRANULARITY = 8192


class BaseEngine(object):
    def get_create_sql(self):
        raise NotImplementedError


class MergeTree(BaseEngine):
    def __init__(self, date_field, primary_keys,
                 granularity=DEFAULT_MERGE_TREE_GRANULARITY):
        self.date_field = date_field
        self.primary_keys = primary_keys
        self.granularity = granularity

    def get_create_sql(self):
        return "MergeTree(%s, (%s), %s)" % (
            self.date_field,
            ", ".join(self.primary_keys),
            self.granularity
        )
