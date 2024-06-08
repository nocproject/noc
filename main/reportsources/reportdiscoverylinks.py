# ---------------------------------------------------------------------
# Discovery Links Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
import polars as pl

# NOC modules
from noc.main.models.pool import Pool
from noc.main.models.report import Report
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import BandData
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.core.datasources.loader import loader
from noc.core.translation import ugettext as _


class ReportDiscoveryLinks(ReportSource):
    name = "reportdiscoverylinks"

    checks = [  # pp, title, condition
        ("status = False", _("All polling"), "1.1"),  # 2is1.6is1.9a2
        ("status = False", "0", "1.1"),  # 2is1.6is1.9a2.3hs0
        ("status = False", "1", "1.1"),  # 2is1.6is1.3hs2
        ("status = False", "2", "1.1"),  # 2is1.6is1.3hs3
        ("status = False", _("More 3"), "1.1"),  # 2is1.6is1.3hs4
    ]

    def get_format(self) -> BandFormat:
        return BandFormat(
            title_template="Profile Check Summary",
            columns=[
                ColumnFormat(name="links_count", title=_("Links count")),
                ColumnFormat(name="mo_count", title=_("MO Count")),
                ColumnFormat(name="percent_at_all", title=_("Percent at All")),
                ColumnFormat(name="detail", title=_("Detail"), format_type="url"),
            ],
        )

    def get_data(self, request=None, **kwargs) -> List[BandData]:
        data = []
        ds = loader["managedobjectds"]
        sql = pl.SQLContext()
        r = ds.query_sync(fields=["pool", "status", "enable_ping", "enable_box", "link_count"])
        sql.register("mo", r.lazy())
        #
        od_report = Report.get_by_code("OBJECT_DETAIL")
        if od_report:
            url = f"/main/reportconfig/{od_report.id}/run?" + "&".join(
                [
                    "output_type=xlsx",
                    "fields=name,address,object_profile,avail,profile,administrativedomain,"
                    "segment,pool,link_count",
                    "detail_query=%s&pool=%s",
                ]
            )
        else:
            url = ""

        SQL = """
         SELECT pool, count(*) as all,
          sum(link_count = 0) as '0', sum(link_count = 1) as '1',
          sum(link_count = 2) as '2', sum(link_count > 2) as 'More 3'
         FROM mo
         WHERE status = True and enable_ping = True and enable_box = True
         GROUP BY pool
         ORDER BY pool
        """
        for row in sql.execute(SQL, eager=True).to_dicts():
            if not row["all"]:
                continue
            pool = Pool.get_by_name(row["pool"])
            b = BandData(name="row")
            b.format = BandFormat(title_template="{{ name }}")
            b.set_data({"name": pool.name})
            data.append(b)
            for x, condition in [
                ("all", ""),
                ("0", "and link_count = 0"),
                ("1", "and link_count = 1"),
                ("2", "and link_count = 2"),
                ("More 3", "and link_count > 2"),
            ]:
                b = BandData(name="row")
                b.set_data(
                    {
                        "links_count": x,
                        "mo_count": row[x],
                        "percent_at_all": (
                            f'{round(row[x] / row["all"] * 100, 2)} %' if x != "all" else ""
                        ),
                        "detail": url
                        % (
                            f"select * from mo where status = True and enable_ping = True and enable_box = True {condition}",
                            str(pool.id),
                        ),
                    }
                )
                data.append(b)
        return data
