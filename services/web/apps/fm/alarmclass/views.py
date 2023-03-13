# ---------------------------------------------------------------------
# fm.alarmclass application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmclasscategory import AlarmClassCategory
from noc.sa.interfaces.base import StringParameter, DictParameter
from noc.core.translation import ugettext as _


class AlarmClassApplication(ExtDocApplication):
    """
    AlarmClass application
    """

    title = _("Alarm Class")
    menu = [_("Setup"), _("Alarm Classes")]
    model = AlarmClass
    parent_model = AlarmClassCategory
    parent_field = "parent"
    query_fields = ["name", "description"]
    query_condition = "icontains"

    @view(
        method=["PUT"],
        url=r"^(?P<aid>[0-9a-f]{24})/localization/?$",
        access="update",
        api=True,
        validate={
            "language": StringParameter(required=True),
            "localization": DictParameter(required=True),
        },
    )
    def api_update_i18n(self, request, aid, language: str, localization: Dict[str, str]):
        ac: AlarmClass = self.get_object_or_404(AlarmClass, id=aid)
        for field in localization:
            if field not in ac.i18n:
                ac.i18n[field] = {language: localization[field]}
            else:
                ac.i18n[field][language] = localization[field]
        ac.update(i18n=ac.i18n)
        return self.render_json({"status": True})
