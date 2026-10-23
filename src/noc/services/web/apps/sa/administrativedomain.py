# ---------------------------------------------------------------------
# sa.administrativedomain application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, api
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _


class AdministrativeDomainApplication(ExtModelApplication):
    """
    AdministrativeDomain application
    """

    title = _("Administrative Domains")
    menu = [_("Setup"), _("Administrative Domains")]
    model = AdministrativeDomain
    query_fields = ["name__icontains", "description__icontains"]
    lookup_default = [{"has_children": False, "id": "Leave unchanged", "label": "Leave unchanged"}]

    def field_object_count(self, o):
        return o.managedobject_set.count()

    def instance_to_lookup(self, o, fields=None):
        return {"id": o.id, "label": str(o), "has_children": o.has_children}

    @api.get(r"^(?P<id>\d+)/get_path/$", access="read")
    def api_get_path(self, request: HttpRequest, id):
        o = self.get_object_or_404(AdministrativeDomain, id=id)
        path = [AdministrativeDomain.objects.get(id=ns) for ns in o.get_path()]
        return {
            "data": [{"level": path.index(p) + 1, "id": str(p.id), "label": p.name} for p in path]
        }
