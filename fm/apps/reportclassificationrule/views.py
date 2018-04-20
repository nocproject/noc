# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Classification Rules Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.fm.models import EventClassificationRule
from noc.sa.models import profile_registry


class ReportForm(forms.Form):
    profile = forms.ChoiceField(label="Profile",
                                choices=profile_registry.choices)

class ReportClassificationRules(SimpleReport):
    title="Classification Rules"
    form = ReportForm

    def get_data(self, profile):
        def get_profile(r):
            for p in r.patterns:
                if p.key_re in ("profile", "^profile$"):
                    return p.value_re
            return None

        data = []
        for r in EventClassificationRule.objects.order_by("preference"):
            p_re = get_profile(r)
            if p_re and not re.search(p_re, profile):
                # Skip
                continue
            data += [SectionRow("%s (%s)"%(r.name, r.preference))]
            data += [["Event Class", r.event_class.name]]
            for p in r.patterns:
                data += [[p.key_re, p.value_re]]
        return self.from_dataset(title=self.title,
                                 columns=["Key RE","Value RE"],
                                 data=data)
