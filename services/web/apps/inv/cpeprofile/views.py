# ---------------------------------------------------------------------
# inv.CPEprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import List, Tuple

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.cpeprofile import CPEProfile
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


class CPEProfileApplication(ExtDocApplication):
    """
    InterfaceProfile application
    """

    title = _("CPE Profile")
    menu = [_("Setup"), _("CPE Profiles")]
    model = CPEProfile
    query_condition = "icontains"
    query_fields = ["name", "description"]
