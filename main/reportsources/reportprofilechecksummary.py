# ---------------------------------------------------------------------
# Profile Check Summary Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict

# Third-party modules
import polars as pl

# NOC modules
from noc.main.models.pool import Pool
from noc.main.models.report import Report
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import Band
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.core.datasources.loader import loader
from noc.core.translation import ugettext as _


class ReportProfileCheckSummary(ReportSource):
    name = "reportprofilechecksummary"

    checks = [  # pp, title, condition
        ("status = False", _("Not Managed"), "1.1"),  # 1is1
        ("status = True and enable_ping = True", _("Is Managed"), "1.2"),  # 2is1
        (
            "status = True and enable_ping = True and enable_box = True",
            _("Is Managed, object type defined"),
            "1.2.1",
        ),  # 2is1.6is1.3isp0
        (
            "status = True and enable_ping = True and enable_box = True and trouble_profile = False and trouble_snmp = False and trouble_cli = True",
            _("Is Managed, object type defined bad CLI Credential"),
            "1.2.1.1",
        ),  # 2is1.6is1.3isp0.2isp1
        (
            "status = True and enable_ping = True and enable_box = True and (trouble_profile = True or trouble_snmp = True)",
            _("Is Managed, object type undefined"),
            "1.2.2",
        ),  # 2is1.6is1.3isp1
        (
            "status = True and enable_ping = True and enable_box = True and avail='no' and (trouble_profile = True or trouble_snmp = True)",
            _("Is Managed, object type undefined not ping response"),
            "1.2.2.1",
        ),  # 2is1.6is1.3isp1.3is1
        (
            "status = True and enable_ping = True and enable_box = True and avail='yes' and (trouble_profile = True or trouble_snmp = True)",
            _("Is Managed, object type undefined has ping response"),
            "1.2.2.2",
        ),  # 2is1.6is1.3isp1.3is2
        (
            "status = True and enable_ping = True and enable_box = True and avail='yes' and trouble_profile = True and trouble_snmp = True",
            _("Is Managed, object type undefined bad SNMP Credential"),
            "1.2.2.2.1",
        ),  # 2is1.6is1.3isp1.3is2.1isp1
        (
            "status = True and enable_ping = True and enable_box = True and avail='yes' and trouble_profile = True and trouble_snmp = False",
            _("Is Managed, object type undefined for various reasons"),
            "1.2.2.2.2",
        ),  # 2is1.6is1.3isp1.3is2.1isp0
        # (_("Is Managed, object type Profile is not know"), "2is1.6is1.9a1.3is2.4isp1"),
        (
            "status = True and enable_ping = False and enable_box = False",
            _("Is monitoring, object type undefined, only availability check"),
            "1.2.3",
        ),  # 2is1.6is2
    ]

    def get_formats(self) -> Dict[str, BandFormat]:
        return {
            "header": BandFormat(
                title_template="Profile Check Summary",
                columns=[
                    ColumnFormat(name="pp", title=_("PP")),
                    ColumnFormat(name="status", title=_("Status")),
                    ColumnFormat(name="quantity", title=_("Quantity")),
                    ColumnFormat(name="percent", title=_("Percent")),
                    ColumnFormat(name="detail", title=_("Detail"), format_type="url"),
                ],
            ),
            "pool": BandFormat(title_template="{{ name }}"),
        }

    def get_data(self, request=None, **kwargs) -> List[Band]:
        data = []
        ds = loader["managedobjectds"]
        sql = pl.SQLContext()
        r = ds.query_sync(
            fields=[
                "pool",
                "status",
                "enable_ping",
                "enable_box",
                "avail",
                "trouble_profile",
                "trouble_snmp",
                "trouble_cli",
            ],
        )
        sql.register("mo", r.lazy())
        #
        od_report = Report.get_by_code("OBJECT_DETAIL")
        if od_report:
            url = f"/main/reportconfig/{od_report.id}/run?" + "&".join(
                [
                    "output_type=xlsx",
                    "fields=name,address,object_profile,avail,profile,administrativedomain,segment,trouble_detail",
                    "detail_query=%s&pool=%s",
                ]
            )
        else:
            url = ""
        # Create SQL
        title_map = {}
        condition_map = {}
        for condition, title, key in self.checks:
            title_map[key] = title
            condition_map[key] = condition
        condition = ",".join(f"sum({c}) as '{a}'" for a, c in condition_map.items())
        pools = [p for p in Pool.objects.filter().order_by("name")] + ["Summary"]
        # Main Loop
        for pool in pools:
            if pool != "Summary":
                b = Band(name="pool", data={"name": pool.name})
                query = f"SELECT {condition} FROM mo WHERE pool = '{pool.name}' GROUP BY pool"
            else:
                b = Band(name="pool", data={"name": "Summary"})
                query = f"SELECT {condition} FROM mo"
            rows = sql.execute(query, eager=True)
            if rows.is_empty():
                data.append(b)
                continue
            for row in rows.transpose(include_header=True).to_dicts():
                if row["column"] == "1.2" and row["column_0"] == 0:
                    data.pop()
                    break
                x = Band(
                    name="row",
                    data={
                        "pp": row["column"],
                        "status": title_map[row["column"]],
                        "quantity": row["column_0"],
                        "percent": "",
                        "detail": url
                        % (
                            f"select * from mo where {condition_map[row['column']]}",
                            str(pool.id) if pool != "Summary" else "",
                        ),
                    },
                )
                if row["column"] == "1.2.1":
                    p = round(row["column_0"] / data[-1].data["quantity"] * 100.0, 2)
                    x.data["percent"] = f"{p} %"
                b.add_child(x)
            data.append(b)
        return data
