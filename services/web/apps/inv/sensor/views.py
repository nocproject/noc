# ----------------------------------------------------------------------
# inv.sensor application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.services.web.base.decorators.state import state_handler
from noc.inv.models.sensor import Sensor
from noc.core.translation import ugettext as _


@state_handler
class SensorApplication(ExtDocApplication):
    """
    ResourceGroup application
    """

    title = "Sensor"
    menu = [_("Setup"), _("Sensor")]
    model = Sensor
    query_fields = ["label"]
    query_condition = "icontains"

    def field_row_class(self, o):
        if o.profile and o.profile.style:
            return o.profile.style.css_class_name
        else:
            return ""

    # def cleaned_query(self, q):
    #     q = super().cleaned_query(q)
    #     if "managed_object" in q:
    #         q["object__in"] = Object.get_managed(q["managed_object"])
    #         del q["managed_object"]
    #     return q
