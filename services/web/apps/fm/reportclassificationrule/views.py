# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Classification Rules Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Django modules
from django import forms
from noc.core.profile.loader import loader as profile_loader
from noc.core.translation import ugettext as _
from noc.fm.models.eventclassificationrule import EventClassificationRule
# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow


class ReportForm(forms.Form):
    profile = forms.ChoiceField(label=_("Profile"),
                                choices=profile_loader.choices())


class ReportClassificationRules(SimpleReport):
    title = _("Classification Rules")
    form = ReportForm

    def get_data(self, request, profile):
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
            data += [SectionRow("%s (%s)" % (r.name, r.preference))]
            data += [["Event Class", r.event_class.name]]
            for p in r.patterns:
                data += [[p.key_re, p.value_re]]
        return self.from_dataset(title=self.title,
                                 columns=["Key RE", "Value RE"],
                                 data=data)
