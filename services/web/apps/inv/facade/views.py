# ----------------------------------------------------------------------
# inv.facade application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.doccategory import DocCategory
from noc.inv.models.facade import Facade
from noc.core.translation import ugettext as _


class FacadeApplication(ExtDocApplication):
    """
    Facade application
    """

    title = _("Facades")
    menu = [_("Setup"), _("Facades")]
    model = Facade
    parent_model = DocCategory
    parent_field = "parent"
    query_fields = ["name__icontains", "description__icontains"]
    glyph = "table"

    @view(url="^(?P<id>[0-9a-f]{24})/facade.svg$", method=["GET"], access="read", api=True)
    def api_svg(self, request, id: str):
        o = self.get_object_or_404(Facade, id)
        return HttpResponse(o.data, content_type="image/svg+xml", status=200)
