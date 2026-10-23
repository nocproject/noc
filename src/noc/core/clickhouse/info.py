# ----------------------------------------------------------------------
# Clickhouse DDL Parser
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections.abc import Iterable
import re

# NOC modules
from noc.core.text import find_balanced
from noc.config import config
from .connect import connection


@dataclass
class TableInfo:
    """
    Parsed DDL info.

    Attributes:
        name: Table name.
        ttl: Table-level TTL in seconds.
    """

    name: str
    table_ttl: int | None = None

    @classmethod
    def from_sql(cls, sql: str) -> "TableInfo":
        """
        Parse ClickHouse DDL SQL.

        Args:
            sql: CREATE TABLE query,
                as is in system.tables create_table_query

        Returns:
            Parsed TableInfo.

        Raises:
            ValueError: if failed to parse.
        """
        create_match = rx_create_table.search(sql)
        if not create_match:
            msg = "no CREATE TABLE statement"
            raise ValueError(msg)
        fields_def_end = find_balanced(sql, start=create_match.end() - 1)
        if fields_def_end == -1:
            msg = "no closing bracket"
            raise ValueError(msg)
        table_name = create_match.group(1)
        if "." in table_name:
            table_name = table_name.split(".")[-1]
        # Parse TTL
        table_ttl = None
        ttl_match = rx_ttl.search(sql, fields_def_end + 1)
        if ttl_match:
            match ttl_match.group(2):
                case "Second":
                    table_ttl = int(ttl_match.group(3))
                case "Day":
                    table_ttl = int(ttl_match.group(3)) * 24 * 3600
                case _ as x:
                    msg = f"invalid ttl measure: {x}"
                    raise ValueError(msg)
        return TableInfo(name=table_name, table_ttl=table_ttl)

    @classmethod
    def iter_for_tables(cls, tables: Iterable[str]) -> "Iterable[TableInfo]":
        """
        Iterate TableInfo for given tables.

        Args:
            tables: Tables to query.

        Returns:
            Yields TableInfo for each table found.
        """
        t = list(tables)
        if not t:
            return
        ch = connection()
        for _table, sql in ch.execute(CH_INFO_SQL, [config.clickhouse.db, t]):
            yield TableInfo.from_sql(sql)


rx_create_table = re.compile(r"CREATE TABLE ([^\(]+?)\s*\(", re.MULTILINE | re.DOTALL)
rx_ttl = re.compile(
    r"\s*TTL\s+(\S+)\s*\+\s*toInterval([^\(]+)\(\s*(\d+)\s*\)", re.MULTILINE | re.DOTALL
)
CH_INFO_SQL = """
SELECT name, create_table_query
FROM system.tables
WHERE database=%s AND name IN (%s)"""
