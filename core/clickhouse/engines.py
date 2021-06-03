# ----------------------------------------------------------------------
# Clickhouse engines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.config import config

DEFAULT_MERGE_TREE_GRANULARITY = config.clickhouse.default_merge_tree_granularity


class BaseEngine(object):
    def get_create_sql(self):
        raise NotImplementedError


class MergeTree(BaseEngine):
    def __init__(self, date_field, primary_keys, granularity=DEFAULT_MERGE_TREE_GRANULARITY):
        self.date_field = date_field
        self.primary_keys = primary_keys
        self.granularity = granularity

    def get_create_sql(self):
        return "MergeTree(%s, (%s), %s)" % (
            self.date_field,
            ", ".join(self.primary_keys),
            self.granularity,
        )


class AggregatingMergeTree(BaseEngine):
    def __init__(
        self, date_field, order_by, primary_keys=None, granularity=DEFAULT_MERGE_TREE_GRANULARITY
    ):
        self.date_field = date_field
        self.primary_keys = primary_keys
        self.order_by = order_by
        self.granularity = granularity

    def get_create_sql(self):
        return (
            f"AggregatingMergeTree() "
            f"PARTITION BY toYYYYMM({self.date_field}) "
            f'PRIMARY KEY ({",".join(self.primary_keys)}) '
            f'ORDER BY ({",".join(self.order_by)}) '
            f"SETTINGS index_granularity = {self.granularity} "
        )
