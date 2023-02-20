# ---------------------------------------------------------------------
# inv.cpe application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.decorators.state import state_handler
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.cpe import CPE
from noc.core.translation import ugettext as _


@state_handler
class CPEApplication(ExtDocApplication):
    """
    inv.CPE application
    """

    title = _("CPEs")
    menu = _("CPEs")
    model = CPE
    query_fields = ["description__contains", "global_id", "global_id__contains"]

    @staticmethod
    def get_style(cpe: CPE):
        profile = cpe.profile
        # try:
        #     return style_cache[profile.id]
        # except KeyError:
        #     pass
        if profile.style:
            s = profile.style.css_class_name
        else:
            s = ""
        # style_cache[profile.id] = s
        return s
