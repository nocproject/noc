# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.reportobgectsportstatus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.lib.text import list_to_ranges
class ReportForm(forms.Form):
    sel = forms.ModelChoiceField(
            label=_("Interface Profile"),
            required=True,
            queryset=InterfaceProfile.objects.order_by("name"))
class ReportIfaceStatus(SimpleReport):
    title = _("Отчет статуса интерфейсов")
    form = ReportForm
    def get_data(self, request, sel):
        data = []
        qs = ManagedObject.objects
        if not request.user.is_superuser:
            qs = ManagedObject.objects.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        columns = [_("Managed Objects"), _("Switch availability status"), _("IP address"), _("Model"), _("Software"), _("Port name"), _("Port status"), _("Link status"), _("VLAN id")]
        ip = InterfaceProfile.objects.get(name=sel.name)
        interf = Interface.objects.filter(profile=ip, type="physical")
        for i in interf:
            si = list(i.subinterface_set.filter(enabled_afi="BRIDGE"))
            if len(si) == 1:
                si = si[0]
            try:
                tagged = (list_to_ranges(si.tagged_vlans).replace(",", ", ")).strip()
                data += [[ i.managed_object.name,
                           "Is available" if i.managed_object.get_status() == True else "Not available",
                           i.managed_object.address,
                           str(i.managed_object.vendor) + " " + str(i.managed_object.platform),
                           "\"" + str(i.managed_object.version) + "\"",
                           i.name,
                           "UP" if i.admin_status == True else "Down",
                           "UP" if i.oper_status == True else "Down",
                           ("U: " + str(si.untagged_vlan) if si.untagged_vlan != None else "" + " T: " + tagged if tagged != "" else "").strip()
                        ]]
            except:
                pass
        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data,
            enumerate=True
        )

