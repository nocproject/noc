# ---------------------------------------------------------------------
# Language Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.language import Language
from noc.services.web.base.extmodelapplication import ExtModelApplication


class LanguageApplication(ExtModelApplication):
    title = _("Languages")
    model = Language
    menu = [_("Setup"), _("Languages")]
    query_fields = ["name__icontains", "native_name__icontains"]
