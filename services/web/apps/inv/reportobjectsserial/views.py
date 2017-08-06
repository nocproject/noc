# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.reportfilter
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    sel = forms.ModelChoiceField(
            label=_("Managed Object Selector"),
            required=True,
            queryset=ManagedObjectSelector.objects.order_by("name"))


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Serial Number")
    form = ReportForm

    def get_data(self, request, sel):

        qs = ManagedObject.objects
        if not request.user.is_superuser:
            qs = ManagedObject.objects.filter(administrative_domain__in=UserAccess.get_domains(request.user))

        # Get all managed objects by selector
        mos_list = qs.filter(sel.Q)

        columns = [_("Managed Objects"), _("Address"), _("Vendor"), _("Platform"),
                   _("HW Revision"), _("SW Version"), _("Serial")]
        data = []

        for mo in mos_list:
            q = Object._get_collection().find({"data.management.managed_object": {"$in": [mo.id]}})
            if q.count() == 0:
                data += [[mo.name,
                          mo.address,
                          mo.vendor or None,
                          mo.get_attr("platform") or None,
                          mo.get_attr("HW version") or None,
                          mo.get_attr("version") or None,
                          mo.get_attr("Serial Number") or None,
                          None
                          ]]
            else:
                for x in q:
                    data += [[x["name"],
                              mo.address,
                              mo.vendor or None,
                              mo.get_attr("platform") or None,
                              mo.get_attr("HW version") or None,
                              mo.get_attr("version") or None,
                              x["data"]["asset"]["serial"]
                              ]]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data,
            enumerate=True
        )
