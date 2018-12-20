# -*- coding: utf8 -*-
"""Report interface status."""
# ---------------------------------------------------------------------
# ip.reportobgectsportstatus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from pymongo import ReadPreference
from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.core.translation import ugettext as _
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject


class ReportForm(forms.Form):
    """Report Form initialized."""

    iprofile = forms.ModelChoiceField(
        label=_("Interface Profile"),
        required=False,
        queryset=InterfaceProfile.objects.order_by("name")
    )
    selector = forms.ModelChoiceField(
        label=_("Managed Object Selector"),
        required=False,
        queryset=ManagedObjectSelector.objects.order_by("name")
    )
    zero = forms.BooleanField(
        label=_("Exclude ports in the status down"),
        required=False,
        initial=True
    )
    defzero = forms.BooleanField(
        label=_("Exclude interfaces with the default profile (for Selector filter)"),
        required=False,
        initial=True
    )


class ReportIfaceStatus(SimpleReport):
    """Create Report form."""

    title = _(u"Report interface status")
    form = ReportForm

    def get_data(self, request, iprofile=None, selector=None, zero=None, defzero=None):
        """Get_data function."""

        def humanize_speed(speed):
            if not speed:
                return "-"
            for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d%s" % (speed // t, n)
                    else:
                        return "%.2f%s" % (float(speed) / t, n)
            return str(speed)

        data = []
        mo = {}
        DUPLEX = {
            True: "Full",
            False: "Half"
        }

        columns = [_("Managed Objects"), _("IP address"), _("Model"), _("Software"),
                   _("Port name"), _("Port status"), _("Link status"), _("Port speed"), _("Port duplex")]
        if selector or iprofile:
            mos = ManagedObject.objects.filter(is_managed=True)
            if selector:
                mos = mos.filter(selector.Q)

            for o in mos:
                mo[o.id] = {
                    "type": "managedobject",
                    "id": str(o.id),
                    "name": o.name,
                    "status": o.is_managed,
                    "address": o.address,
                    "vendor": o.vendor,
                    "version": o.version,
                    "platform": o.platform
                }
            match = {
                "managed_object": {
                    "$in": list(mo)
                },
                "type": {
                    "$in": ["physical"]
                },
                "admin_status": True
            }

            if iprofile:
                match["profile"] = {
                    "$in": [iprofile.id]
                }
            if zero:
                match["oper_status"] = True

            if selector and defzero:
                def_prof = [pr.id for pr in InterfaceProfile.objects.filter(name__contains="default")]
                match["profile"] = {
                    "$nin": def_prof
                }

            for i in Interface._get_collection().with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).\
                    aggregate([{"$match": match}]):
                data += [[mo[i['managed_object']]['name'],
                          mo[i['managed_object']]['address'],
                          "%s %s" % (str(mo[i['managed_object']]['vendor']),
                                     str(mo[i['managed_object']]['platform'])),
                          str(mo[i['managed_object']]['version']),
                          i['name'],
                          "UP" if i['admin_status'] is True else "Down",
                          "UP" if "oper_status" in i and i['oper_status'] is True else "Down",
                          humanize_speed(i['in_speed']) if "in_speed" in i else "-",
                          DUPLEX.get(i['full_duplex']) if "full_duplex" in i and "in_speed" in i else "-"]]

            return self.from_dataset(title=self.title, columns=columns, data=data, enumerate=True)
        else:
            return self.from_dataset(title=self.title, columns=[_("Nothing")], data=[["Nothing selected, try again"]])
