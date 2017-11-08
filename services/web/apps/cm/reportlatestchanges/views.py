# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Latest Change Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import datetime

from django import forms
from noc.cm.models import Object
from noc.core.translation import ugettext as _
from noc.lib.app.simplereport import SimpleReport, TableColumn


#
# Report Form
#
class ReportForm(forms.Form):
    repo = forms.ChoiceField(label=_("Type"), choices=[("prefix-list", "prefix-list")])
    days = forms.IntegerField(label=_("In Days"), min_value=1)


#
#
#
class ReportreportLatestChanges(SimpleReport):
    title = _("Latest Changes")
    form = ReportForm

    def get_data(self, repo, days, **kwargs):
        oc = Object.get_object_class(repo)
        baseline = datetime.datetime.now() - datetime.timedelta(days=days)
        return self.from_dataset(
            title="%s: %s in %d days" % (self.title, repo, days),
            columns=[
                "Object",
                TableColumn(_("Last Changed"), format="datetime")],
            data=[(o, o.last_modified) for o in
                  oc.objects.filter(last_modified__gte=baseline).order_by("-last_modified")],
            enumerate=True)
