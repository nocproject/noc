# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Classification Rules Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.fm.models import EventClassificationRule


class ReportClassificationRules(SimpleReport):
    title="Classification Rules"

    def get_data(self, **kwargs):
        data=[]
        for r in EventClassificationRule.objects.order_by("preference"):
            data += [SectionRow("%s (%s)"%(r.name, r.preference))]
            data += [["Event Class", r.event_class.name]]
            for p in r.patterns:
                data += [[p.key_re, p.value_re]]
        return self.from_dataset(title=self.title,
                                 columns=["Key RE","Value RE"],
                                 data=data)
