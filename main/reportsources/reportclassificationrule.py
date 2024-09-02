# ---------------------------------------------------------------------
# Classification Rules Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import List

# NOC modules
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import BandData
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.fm.models.eventclassificationrule import EventClassificationRule


class ReportClassificationRule(ReportSource):
    name = "reportclassificationrule"

    def get_format(self) -> BandFormat:
        return BandFormat(
            title_template="Classification Rules",
            header_only=True,
            columns=[
                ColumnFormat(name="key_re", title="Key RE"),
                ColumnFormat(name="value_re", title="Value RE"),
            ],
        )

    def get_data(self, request=None, **kwargs) -> List[BandData]:
        def get_profile(r):
            for p in r.patterns:
                if p.key_re in ("profile", "^profile$"):
                    return p.value_re
            return None

        profile = kwargs.get("profile")
        if isinstance(profile, str):
            # For test running
            from noc.sa.models.profile import Profile

            profile = Profile.get_by_name(profile)
        data = []
        for r in EventClassificationRule.objects.order_by("preference"):
            p_re = get_profile(r)
            if profile and p_re and not re.search(p_re, profile.name):
                # Skip
                continue
            # d1
            b = BandData(name="row")
            b.set_data({"name": r.name, "preference": r.preference})
            b.format = BandFormat(title_template="{{ name }} ({{ preference }})")
            data.append(b)
            # d2
            b = BandData(name="row")
            b.set_data({"key_re": "Event Class", "value_re": r.event_class.name})
            data.append(b)
            # data += [SectionRow("%s (%s)" % (r.name, r.preference))]
            # data += [["Event Class", r.event_class.name]]
            for p in r.patterns:
                b = BandData(name="row")
                b.set_data({"key_re": p.key_re, "value_re": p.value_re})
                data.append(b)
        return data
