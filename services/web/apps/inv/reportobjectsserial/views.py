# ---------------------------------------------------------------------
# ip.reportfilter
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django import forms

# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.object import Object
from noc.inv.models.platform import Platform
from noc.inv.models.vendor import Vendor
from noc.inv.models.firmware import Firmware
from noc.lib.app.reportdatasources.report_objectattributes import ReportObjectAttributes
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    sel = forms.ModelChoiceField(
        label=_("Managed Object Selector"),
        required=True,
        queryset=ManagedObjectSelector.objects.order_by("name"),
    )


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Serial Number")
    form = ReportForm

    def get_data(self, request, sel=None):

        qs = ManagedObject.objects
        if not request.user.is_superuser:
            qs = ManagedObject.objects.filter(
                administrative_domain__in=UserAccess.get_domains(request.user)
            )

        # Get all managed objects by selector
        mos_list = qs.filter(sel.Q)

        columns = [
            _("Managed Objects"),
            _("Address"),
            _("Vendor"),
            _("Platform"),
            _("HW Revision"),
            _("SW Version"),
            _("Serial"),
        ]
        data = []
        mos = {
            x["id"]: x
            for x in mos_list.values("id", "name", "address", "vendor", "platform", "version")
        }
        ra = ReportObjectAttributes(sorted(mos))
        ra = ra.get_dictionary()
        objects_serials = {}
        for o in Object._get_collection().aggregate(
            [
                {
                    "$match": {
                        "data": {
                            "$elemMatch": {"attr": "managed_object", "value": {"$in": list(mos)}}
                        }
                    }
                },
                {
                    "$project": {
                        "data": {
                            "$filter": {
                                "input": "$data",
                                "cond": {"$in": ["$$this.attr", ["serial", "managed_object"]]},
                            }
                        }
                    }
                },
            ]
        ):
            if len(o["data"]) < 2:
                continue
            if o["data"][0]["attr"] == "serial":
                objects_serials[int(o["data"][1]["value"])] = o["data"][0]["value"]
            else:
                objects_serials[int(o["data"][0]["value"])] = o["data"][1]["value"]

        for mo in mos.values():
            platform = Platform.get_by_id(mo["platform"]) if mo.get("platform") else None
            vendor = Vendor.get_by_id(mo["vendor"]) if mo.get("vendor") else None
            version = Firmware.get_by_id(mo["version"]) if mo.get("version") else None
            sn, hw = ra[mo["id"]][:2] if mo["id"] in ra else (None, None)
            if mo["id"] in objects_serials:
                sn = objects_serials[mo["id"]]
            data += [
                [
                    mo["name"],
                    mo["address"],
                    vendor,
                    platform,
                    hw,
                    version,
                    sn,
                    None,
                ]
            ]

        return self.from_dataset(title=self.title, columns=columns, data=data, enumerate=True)
