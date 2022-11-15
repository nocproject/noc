# ---------------------------------------------------------------------
# Report Discovery Link Summary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from collections import defaultdict

# NOC modules
from noc.services.web.base.simplereport import (
    SimpleReport,
    PredefinedReport,
    SectionRow,
    TableColumn,
)
from noc.services.web.base.reportdatasources.base import ReportModelFilter
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Discovery Links Summary")
    predefined_reports = {"default": PredefinedReport(_("Discovery Links Summary"), {})}

    save_perc = None

    def calc_percent(self, column, val):
        if column != _("All polling"):
            if val == 0 or self.save_perc == 0:
                return "%.2f %%" % 100
            else:
                r = "%.2f %%" % ((val / float(self.save_perc)) * 100)
            # self.save_perc = None
            return r
        elif column == _("All polling"):
            self.save_perc = val
        return ""

    def get_data(self, request, **kwargs):
        columns, columns_desr = [], []

        r_map = [
            (_("All polling"), "2is1.6is1.9a2"),  # "Is Managed, object type defined"
            (_("0"), "2is1.6is1.9a2.3hs0"),  # "Has 0 Links w type defined"
            (_("1"), "2is1.6is1.3hs2"),  # "Has 1 links"
            (_("2"), "2is1.6is1.3hs3"),  # "Has 2 links"
            (_("More 3"), "2is1.6is1.3hs4"),  # "Has more 3 links"
        ]
        for x, y in r_map:
            columns += [y]
            columns_desr += [x]
        report = ReportModelFilter()
        result = report.proccessed(",".join(columns))

        summary = defaultdict(int)
        data = []
        # url = "/sa/reportstat/repstat_download/?report=%s"
        url = "/sa/reportobjectdetail/download/?" + "&".join(
            [
                "o_format=xlsx",
                "columns=object_name,object_address,object_profile,object_status,profile_name,admin_domain,segment",
                "detail_stat=%s&pool=%s",
            ]
        )
        for p in Pool.objects.filter().order_by("name"):
            m = []
            moss = set(ManagedObject.objects.filter(pool=p).values_list("id", flat=True))
            for col in columns:
                m += [len(result[col.strip()].intersection(moss))]
                summary[col] += m[-1]
            data += [SectionRow(name=p.name)]
            data += [
                (x, y, self.calc_percent(x, y), url % (columns[columns_desr.index(x)], p.name))
                for x, y in zip(columns_desr, m)
            ]
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Links count"),
                _("MO Count"),
                _("Percent at All"),
                TableColumn(_("Detail"), format="url"),
            ],
            data=data,
        )
