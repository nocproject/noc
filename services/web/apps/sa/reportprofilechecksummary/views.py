# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.reportprofilechecksummary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, PredefinedReport, TableColumn
from noc.lib.app.reportdatasources.base import ReportModelFilter
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Profile Check Summary")
    predefined_reports = {
        "default": PredefinedReport(
            _("Managed Object Profile Check Summary"), {}
        )
    }

    save_perc = None

    def calc_percent(self, column, val):
        if column == _("Is Managed, object type defined"):
            if val == 0:
                return "%.2f %%" % 100
            else:
                r = "%.2f %%" % ((val / float(self.save_perc)) * 100)
            self.save_perc = None
            return r
        elif column == _("Is Managed"):
            self.save_perc = val
        return ""

    def get_data(self, request, report_type=None, **kwargs):

        columns, columns_desr = [], []
        sc_code = ["1.1", "1.2", "1.2.1", "1.2.1.1", "1.2.2", "1.2.2.1", "1.2.2.2",
                   "1.2.2.2.1", "1.2.2.2.2", "1.2.2.2.2.1"]
        r_map = [
            (_("Not Managed"), "1is1"),
            (_("Is Managed"), "2is1"),
            # (_("Is Managed not monitoring"), "2is2"),
            # (_("Is monitoring"), "2is1"),
            (_("Is Managed, object type defined"), "2is1.3isp0"),
            (_("Is Managed, object type defined bad CLI Credential"), "2is1.3isp0.2isp1"),
            (_("Is Managed, object type undefined"), "2is1.3isp1"),
            (_("Is Managed, object type undefined not ping response"), "2is1.3isp1.3is1"),
            (_("Is Managed, object type undefined has ping response"), "2is1.3isp1.3is2"),
            (_("Is Managed, object type undefined bad SNMP Credential"), "2is1.3isp1.3is2.1isp1"),
            (_("Is Managed, object type undefined for various reasons"), "2is1.3isp1.3is2.1isp0"),
            (_("Is Managed, object type Profile is not know"), "2is1.7a1.3is2.4isp1")
        ]

        for x, y in r_map:
            columns += [y]
            columns_desr += [x]
        report = ReportModelFilter()
        result = report.proccessed(",".join(columns))

        # result = stat.proccessed(",".join(columns))
        # result = stat.api_result(",".join(columns))
        summary = defaultdict(int)
        data = []
        # url = "/sa/reportstat/repstat_download/?report=%s"
        url = "/sa/reportobjectdetail/download/?" + "&".join([
            "o_format=xlsx",
            "columns=object_name,object_address,object_profile,object_status,profile_name,admin_domain,segment",
            "detail_stat=%s&pool=%s"
        ])
        for p in Pool.objects.filter().order_by("name"):
            m = []
            moss = set(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))
            for col in columns:
                m += [len(result[col.strip()].intersection(moss))]
                summary[col] += m[-1]
            data += [SectionRow(name=p.name)]
            data += [(sc, x, y, self.calc_percent(x, y), url % (columns[columns_desr.index(x)], p.name))
                     for sc, x, y in zip(sc_code, columns_desr, m)]
            data += [("1.2.2.2.2.2", _("Is Managed, objects not processed yet"), 0, "")]
        data += [SectionRow(name="Summary")]
        summary = [summary[k] for k in columns]
        data += [(sc, x, y, self.calc_percent(x, y), url % (columns[columns_desr.index(x)], ""))
                 for sc, x, y in zip(sc_code, columns_desr, summary)]
        data += [("1.2.2.2.2.2", _("Is Managed, objects not processed yet"), 0, "")]
        # columns = ["ID", "Value", "Percent", TableColumn(_("Detail"), format="url")]
        columns = [_("PP"),
                   _("Status"),
                   _("Quantity"),
                   _("Percent"),
                   TableColumn(_("Detail"), format="url")]

        return self.from_dataset(title=self.title, columns=columns, data=data)
