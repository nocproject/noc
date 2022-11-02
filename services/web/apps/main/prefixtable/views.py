# ---------------------------------------------------------------------
# main.prefixtable application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication, view
from noc.services.web.app.modelinline import ModelInline
from noc.main.models.prefixtable import PrefixTable, PrefixTablePrefix
from noc.main.models.label import Label
from noc.sa.interfaces.base import IPParameter, ListOfParameter, ModelParameter
from noc.core.translation import ugettext as _


class PrefixTableApplication(ExtModelApplication):
    """
    PrefixTable application
    """

    title = _("Prefix Table")
    menu = [_("Setup"), _("Prefix Tables")]
    model = PrefixTable

    prefixes = ModelInline(PrefixTablePrefix)

    @view(
        url="^actions/test/$",
        method=["POST"],
        access="update",
        api=True,
        validate={"ids": ListOfParameter(element=ModelParameter(PrefixTable)), "ip": IPParameter()},
    )
    def api_action_test(self, request, ids, ip):
        return {
            "ip": ip,
            "result": [{"id": pt.id, "name": pt.name, "result": ip in pt} for pt in ids],
        }

    def bulk_field_match_labels(self, data):
        if not data:
            return data
        prefix_filters = (d["id"] for d in data)
        labels = defaultdict(list)
        for ll in Label.objects.filter(match_prefixfilter__prefix_table__in=prefix_filters):
            for pf in ll.match_prefixfilter:
                labels[pf.prefix_table.id] += [
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
                        "scope": pf.scope,
                        "is_persist": True,
                    }
                ]
        for row in data:
            row["match_labels"] = labels.get(row["id"], [])
        return data
