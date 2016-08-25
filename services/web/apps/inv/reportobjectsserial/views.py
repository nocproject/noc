# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## ip.reportfilter
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from django import forms
from noc.lib.app.simplereport import SimpleReport, TableColumn, SectionRow
from noc.main.models import CustomField
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.core.translation import ugettext as _
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject



class ReportFilterApplication(SimpleReport):
    title = "MO Serial"

    def get_form(self):
        class RForm(forms.Form):
            mos = forms.ModelChoiceField(
                label=_("Managed Object Selector"),
                required=True,
                queryset=ManagedObjectSelector.objects.order_by("name"))

        self.customize_form(RForm, "mo_sel", search=True)
        return RForm

    def get_data(self, **kwargs):

        cf = CustomField.table_fields("ip_prefix")
        q = {}
        for k in kwargs:
            v = kwargs[k]
            if v:
                if k == "description":
                    q[k + "__icontains"] = v
                else:
                    q[k] = v

        # Get all managed objects
        mos_list = ManagedObject.objects.filter(q["mos"].Q)
        mos_list = [x.id for x in mos_list]

        # data = Object._get_collection().find({"data.management.managed_object": {"$in":[6840]}})
        q = Object._get_collection().find({"data.management.managed_object": {"$in": mos_list}})

        columns = ["Managed Objects", "PartNo", "Serial"]
        data = []
        for x in q:
            data += [[x["name"],
            ObjectModel.objects.filter(id=x["model"])[0],
            x["data"]["asset"]["serial"]
            ]]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data
        )
