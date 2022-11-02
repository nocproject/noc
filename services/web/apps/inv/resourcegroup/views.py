# ----------------------------------------------------------------------
# inv.resourcegroup application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, List

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.comp import smart_text
from noc.main.models.label import MATCH_BADGES, MATCH_OPS
from noc.core.translation import ugettext as _


def clean_label(label: str) -> Tuple[str, str, List[str]]:
    r = label.split("::")
    badges = []
    if len(r) == 1:
        return "", label, badges
    if r[0] == "noc":
        r.pop(0)
    if r[-1] in MATCH_OPS:
        badges += [MATCH_BADGES[r[-1]]]
        r.pop(-1)
    return "::".join(r[:-1]), r[-1], badges


class ResourceGroupApplication(ExtDocApplication):
    """
    ResourceGroup application
    """

    title = "ResourceGroup"
    menu = [_("Resource Groups")]
    model = ResourceGroup
    glyph = "object-group"
    query_fields = ["name", "description"]
    query_condition = "icontains"

    @staticmethod
    def field_service_expression(o: "ResourceGroup"):
        r = []
        for num, ml in enumerate(o.dynamic_service_labels):
            if num:
                r += [
                    {
                        "id": "&&",
                        "is_protected": False,
                        "scope": "",
                        "name": "&&",
                        # "name": ll.name,
                        "value": "&&",
                        "badges": [],
                        "bg_color1": 0,
                        "fg_color1": 16777215,
                        "bg_color2": 0,
                        "fg_color2": 16777215,
                    }
                ]
            for ll in ml.get_labels():
                scope, value, badges = clean_label(ll.name)
                r += [
                    {
                        "id": ll.name,
                        "is_protected": ll.is_protected,
                        "scope": scope,
                        "name": f" {scope}::{value}" if scope else value,
                        "value": value,
                        "badges": ll.badges + badges,
                        # "bg_color1": f"#{ll.bg_color1:06x}",
                        # "fg_color1": f"#{ll.fg_color1:06x}",
                        # "bg_color2": f"#{ll.bg_color2:06x}",
                        # "fg_color2": f"#{ll.fg_color2:06x}",
                        "bg_color1": ll.bg_color1,
                        "fg_color1": ll.fg_color1,
                        "bg_color2": ll.bg_color2,
                        "fg_color2": ll.fg_color2,
                    }
                ]

        return r

    @staticmethod
    def field_client_expression(o: "ResourceGroup"):
        r = []
        for ml in o.dynamic_client_labels:
            for ll in ml.get_labels():
                scope, value, badges = clean_label(ll.name)
                r += [
                    {
                        "id": ll.name,
                        "is_protected": ll.is_protected,
                        "scope": scope,
                        "name": f"{scope}::{value}" if scope else value,
                        "value": value,
                        "badges": ll.badges,
                        "bg_color1": ll.bg_color1,
                        "fg_color1": ll.fg_color1,
                        "bg_color2": ll.bg_color2,
                        "fg_color2": ll.fg_color2,
                        # "bg_color1": f"#{ll.bg_color1:06x}",
                        # "fg_color1": f"#{ll.fg_color1:06x}",
                        # "bg_color2": f"#{ll.bg_color2:06x}",
                        # "fg_color2": f"#{ll.fg_color2:06x}",
                    }
                ]
        return r

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": smart_text(o), "has_children": o.has_children}

    @view("^(?P<id>[0-9a-f]{24})/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(ResourceGroup, id=id)
        path = [ResourceGroup.get_by_id(rg) for rg in o.get_path()]
        return {
            "data": [
                {"level": level + 1, "id": str(p.id), "label": smart_text(p.name)}
                for level, p in enumerate(path)
            ]
        }
