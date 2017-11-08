# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.networksegment application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.networksegment import NetworkSegment
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess


class NetworkSegmentApplication(ExtDocApplication):
    """
    NetworkSegment application
    """
    title = _("Network Segment")
    menu = [_("Setup"), _("Network Segments")]
    model = NetworkSegment
    query_fields = ["name__icontains", "description__icontains"]

    def queryset(self, request, query=None):
        qs = super(NetworkSegmentApplication, self).queryset(request, query)
        if not request.user.is_superuser:
            qs = qs.filter(adm_domains__in=UserAccess.get_domains(request.user))
        return qs

    def instance_to_lookup(self, o, fields=None):
        return {
            "id": str(o.id),
            "label": unicode(o),
            "has_children": o.has_children
        }

    def field_count(self, o):
        return ManagedObject.objects.filter(segment=o).count()

    @view("^(?P<id>[0-9a-f]{24})/get_path/$",
          access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(NetworkSegment, id=id)
        path = [NetworkSegment.objects.get(id=ns) for ns in o.get_path()]
        return {"data": [{"level": path.index(p) + 1, "id": str(p.id), "label": unicode(p.name)} for p in path]}

    @view("^(?P<id>[0-9a-f]{24})/effective_settings/$",
          access="read", api=True)
    def api_effective_settings(self, request, id):
        o = self.get_object_or_404(NetworkSegment, id=id)
        return o.effective_settings
