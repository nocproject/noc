# ---------------------------------------------------------------------
# vc.vlanfilter application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.vlanfilter import VLANFilter
from noc.sa.interfaces.base import IntParameter
from noc.main.models.label import Label
from noc.core.translation import ugettext as _


class VLANFilterApplication(ExtDocApplication):
    """
    VLANFilter application
    """

    title = _("VLAN Filter")
    menu = [_("Setup"), _("VLAN Filters")]
    model = VLANFilter

    def bulk_field_match_labels(self, data):
        if not data:
            return data
        vlan_filters = (str(d["id"]) for d in data)
        labels = defaultdict(list)
        for ll in Label.objects.filter(match_vlanfilter__vlan_filter__in=vlan_filters):
            for vf in ll.match_vlanfilter:
                labels[str(vf.vlan_filter.id)] += [
                    {
                        "labels": [
                            {
                                "id": ll.name,
                                "is_protected": ll.is_protected,
                                "scope": ll.scope,
                                "name": ll.name,
                                "value": ll.value,
                                "badges": ll.badges,
                                "bg_color1": f"#{ll.bg_color1:06x}",
                                "fg_color1": f"#{ll.fg_color1:06x}",
                                "bg_color2": f"#{ll.bg_color2:06x}",
                                "fg_color2": f"#{ll.fg_color2:06x}",
                            }
                        ],
                        "scope": vf.scope,
                        "is_persist": False,
                    }
                ]
        for row in data:
            row["match_labels"] = labels.get(str(row["id"]), [])
        return data

    def lookup_vc(self, q, name, value):
        """
        Resolve __vc lookups
        :param q:
        :param name:
        :param value:
        :return:
        """
        value = IntParameter().clean(value)
        filters = [str(f.id) for f in VLANFilter.objects.filters(include_vlans__in=[value])]
        if filters:
            x = "(id IN (%s))" % ", ".join(filters)
        else:
            x = "FALSE"
        try:
            q[None] += [x]
        except KeyError:
            q[None] = [x]
