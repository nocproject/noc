# ---------------------------------------------------------------------
# support.crashinfo application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import uuid

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.support.models.crashinfo import Crashinfo
from noc.core.translation import ugettext as _


class CrashinfoApplication(ExtDocApplication):
    """
    Crashinfo application
    """

    title = _("Crashinfo")
    menu = _("Crashinfo")
    model = Crashinfo

    @api.get(r"^(?P<id>\S+)/traceback/", access="read")
    def api_traceback(self, request: HttpRequest, id):
        ci = self.get_object_or_404(Crashinfo, uuid=uuid.UUID(id))
        return ci.traceback
