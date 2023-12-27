# ---------------------------------------------------------------------
# inv.cpe application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
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
    query_fields = ["description__contains", "global_id", "global_id__contains", "address", "label"]

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

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if not isinstance(o, CPE):
            return r
        if o.controller:
            r["controller"] = o.controller.managed_object.id
            r["controller__label"] = o.controller.managed_object.name
            r["local_id"] = o.controller.local_id
        return r

    def cleaned_query(self, q):
        if "controller" in q:
            q["controllers__match"] = {
                "managed_object": int(q.pop("controller")),
                "is_active": True,
            }
        # Clean other
        return super().cleaned_query(q)
