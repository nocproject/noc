# ----------------------------------------------------------------------
# main.chpolicy application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections.abc import Iterable

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.main.models.chpolicy import CHPolicy
from noc.core.translation import ugettext as _
from noc.config import config
from noc.core.clickhouse.connect import connection


@dataclass
class TableStats:
    table: str
    rows: int
    size: int


class CHPolicyApplication(ExtDocApplication):
    """
    CHPolicy application
    """

    title = "CHPolicy"
    menu = [_("Setup"), _("CH Policies")]
    model = CHPolicy
    query_fields = ["table__icontains"]

    def apply_bulk_fields(self, data):
        tables = [row.get("table") for row in data if "table" in row]
        if tables:
            stats = {ts.table: ts for ts in self.iter_table_stats(tables)}
            for row in data:
                ts = stats.get(row["table"])
                if ts:
                    row["rows"] = ts.rows
                    row["size"] = ts.size
        return super().apply_bulk_fields(data)

    @classmethod
    def iter_table_stats(cls, tables: Iterable[str]) -> Iterable[TableStats]:
        sql = """
            SELECT
                t.name AS table,
                SUM(p.rows) AS rows,
                SUM(p.bytes_on_disk) AS size
            FROM
                system.tables AS t
                LEFT JOIN system.parts AS p ON p.database = t.database
                AND p.table = t.name
                AND p.active
            WHERE
                t.database = %s
                AND t.name IN (%s)
            GROUP BY t.name
        """
        ch = connection()
        for table, rows, size in ch.execute(sql, [config.clickhouse.db, list(tables)]):
            yield TableStats(table=table, rows=int(rows), size=int(size))
