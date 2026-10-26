# ----------------------------------------------------------------------
# inv.channel application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.core.feature import Feature
from noc.core.resource import resource_label
from noc.core.techdomain.mapper.base import mapper_loader
from noc.core.translation import ugettext as _
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import ConstraintItem, Endpoint, UsageItem
from noc.services.web.base.docinline import DocInline
from noc.services.web.base.extdocapplication import ExtDocApplication, api


def get_usage(v: list[UsageItem] | None) -> list[dict[str, str]]:
    if not v:
        return []
    return [i.to_json() for i in v]


def get_constraints(v: list[ConstraintItem] | None) -> list[dict[str, list[str]]]:
    if not v:
        return []
    return [i.to_json() for i in v]


class EndpointDocInline(DocInline):
    field_labels = {"resource": resource_label}
    render_fields = {"used_by": get_usage, "constraints": get_constraints}


class ChannelApplication(ExtDocApplication):
    """
    Channel application
    """

    title = _("Channels")
    menu = [_("Channels")]
    model = Channel
    glyph = "road"
    endpoints = EndpointDocInline(Endpoint)
    parent_model = Channel
    parent_field = "parent"
    query_fields = ["name__icontains"]
    require_feature = Feature.CHANNEL

    @api.get("^(?P<id>[0-9a-f]{24})/viz/", access="read")
    def api_viz(self, request: HttpRequest, id: str):
        channel = self.get_object_or_404(Channel, id=id)
        mapper = mapper_loader.get(channel.tech_domain.code)(channel)
        data = mapper.to_viz()
        return self.render_json({"data": data})
