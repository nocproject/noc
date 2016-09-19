# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Failed Scripts Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Failed Discovery")

    def get_form(self):
        class RForm(forms.Form):
            pool = forms.ModelChoiceField(
                label=_("Managed Objects Pools"),
                required=True,
                queryset=Pool.objects.order_by("name"))

        self.customize_form(RForm, "mo_pool", search=True)
        return RForm

    def get_data(self, **kwargs):
        q = {}
        for k in kwargs:
            v = kwargs[k]
            if v:
                if k == "description":
                    q[k + "__icontains"] = v
                else:
                    q[k] = v

        data = []
        job_logs = get_db()["noc.joblog"].find({"$and": [{"problems": {"$ne": {  }}},
                                                         {"problems": {"$exists": "true"}}]})

        for discovery in job_logs:
            mo = ManagedObject.objects.filter(id=int(discovery["_id"].split("-")[2]), pool=q["pool"])
            if not mo:
                continue
            for method in discovery["problems"]:

                data += [
                    (
                        mo[0].name,
                        mo[0].address,
                        method,
                        discovery["problems"][method]
                    )
                ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"),
                _("Discovery"), _("Error")
            ],
            data=data)
