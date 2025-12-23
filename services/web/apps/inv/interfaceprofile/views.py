# ---------------------------------------------------------------------
# inv.interfaceprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import List, Tuple

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.interfaceprofile import InterfaceProfile
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


class InterfaceProfileApplication(ExtDocApplication):
    """
    InterfaceProfile application
    """

    title = _("Interface Profile")
    menu = [_("Setup"), _("Interface Profiles")]
    model = InterfaceProfile
    query_condition = "icontains"
    query_fields = ["name", "description"]

    @staticmethod
    def field_match_expression(o: "InterfaceProfile"):
        r = []
        for num, ml in enumerate(o.match_rules):
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
            r += [
                {
                    "id": "&&",
                    "is_protected": False,
                    "scope": "",
                    "name": f"{ml.dynamic_order}",
                    # "name": ll.name,
                    "value": f"{ml.dynamic_order}",
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
