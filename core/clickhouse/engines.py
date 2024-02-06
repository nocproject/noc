# ----------------------------------------------------------------------
# Clickhouse engines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Tuple

# NOC modules
from noc.config import config

DEFAULT_MERGE_TREE_GRANULARITY = config.clickhouse.default_merge_tree_granularity


class BaseEngine(object):
    def get_create_sql(self):
        raise NotImplementedError


class MergeTree(BaseEngine):
    def __init__(
        self,
        date_field: str,
        order_by: Tuple[str, ...],
        primary_keys: Optional[Tuple[str, ...]] = None,
        partition_function: Optional[str] = None,
        granularity=DEFAULT_MERGE_TREE_GRANULARITY,
    ):
        self.date_field = date_field
        self.partition_function = partition_function
        self.primary_keys = primary_keys
        self.order_by = order_by
        self.granularity = granularity

    def get_create_sql(self):
        sql = ["MergeTree() "]
        if self.partition_function:
            sql += [f"PARTITION BY {self.partition_function} "]
        elif self.date_field:
            sql += [f"PARTITION BY toYYYYMM({self.date_field}) "]
        if self.primary_keys:
            sql += [f'PRIMARY KEY ({",".join(self.primary_keys)}) ']
        sql += [
            f'ORDER BY ({",".join(self.order_by)}) ',
            f"SETTINGS index_granularity = {self.granularity} ",
        ]
        return "".join(sql)


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


class ReplacingMergeTree(BaseEngine):
    def __init__(
        self, date_field, order_by, version_field=None, granularity=DEFAULT_MERGE_TREE_GRANULARITY
    ):
        self.date_field = date_field
        self.version_field = version_field
        self.order_by = order_by
        self.granularity = granularity

    def get_create_sql(self):
        f_version = ""
        if self.version_field:
            f_version = ", ".join(self.version_field)
        partition = ""
        if self.date_field:
            partition = f"PARTITION BY toYYYYMM({self.date_field}) "
        return (
            f"ReplacingMergeTree({f_version}) "
            f"{partition} "
            f'ORDER BY ({",".join(self.order_by)}) '
            f"SETTINGS index_granularity = {self.granularity} "
        )
