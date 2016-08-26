# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## ip.reportfilter
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from django import forms
from noc.lib.app.simplereport import SimpleReport
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.core.translation import ugettext as _
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject



class ReportFilterApplication(SimpleReport):
    title = "ManagedObject Serial Number"

    def get_form(self):
        class RForm(forms.Form):
            sel = forms.ModelChoiceField(
                label=_("Managed Object Selector"),
                required=True,
                queryset=ManagedObjectSelector.objects.order_by("name"))

        self.customize_form(RForm, "mo_sel", search=True)
        return RForm

    def get_data(self, **kwargs):

        # cf = CustomField.table_fields("ip_prefix")
        q = {}
        for k in kwargs:
            v = kwargs[k]
            if v:
                if k == "description":
                    q[k + "__icontains"] = v
                else:
                    q[k] = v

        # Get all managed objects by selector
        mos_list = ManagedObject.objects.filter(q["sel"].Q)

        columns = ["Managed Objects", "Address", "Platform", "SW Version", "Serial"]
        data = []

        for mo in mos_list:
            q = Object._get_collection().find({"data.management.managed_object": {"$in": [mo.id]}})
            if q.count() == 0:
                data += [[mo.name,
                          mo.address,
                          mo.get_attr("platform") or None,
                          mo.get_attr("version") or None,
                          None
                          ]]
            else:
                for x in q:
                    data += [[x["name"],
                              mo.address,
                              mo.get_attr("platform") or None,
                              mo.get_attr("version") or None,
                              x["data"]["asset"]["serial"]
                              ]]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data,
            enumerate=True
        )
