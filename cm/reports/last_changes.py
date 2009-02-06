# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
from noc.cm.models import Object
from django import forms
import datetime

class ReportForm(forms.Form):
    repo=forms.ChoiceField(label="Type",choices=[("config","config"),("dns","dns"),("prefix-list","prefix-list")])
    days=forms.IntegerField(label="In Days",min_value=1)

class Report(noc.main.report.Report):
    name="cm.last_changes"
    title="Latest Changes"
    form_class=ReportForm
    columns=[
            Column("Object",format=lambda o:"<A HREF='/cm/view/%s/%s/'>%s</A>"%(o.repo_name,o.id,o.repo_path)),
            Column("Last Changed")
            ]
    
    def get_queryset(self):
        oc=Object.get_object_class(self.form.cleaned_data["repo"])
        baseline=datetime.datetime.now()-datetime.timedelta(days=self.form.cleaned_data["days"])
        r=[(o,o.last_modified) for o in oc.objects.filter(last_modified__gte=baseline).order_by("-last_modified")]
        return r
