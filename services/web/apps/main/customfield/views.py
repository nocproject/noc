# ---------------------------------------------------------------------
# main.customfield application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.main.models.customfield import CustomField
from noc.core.translation import ugettext as _


class CustomFieldApplication(ExtModelApplication):
    """
    CustomField application
    """

    title = _("Custom Fields")
    menu = [_("Setup"), _("Custom Fields")]
    model = CustomField
    icon = "icon_cog_add"
    query_fields = ["name", "description", "table"]

    def field_table__label(self, obj):
        return obj.table
