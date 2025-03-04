# ----------------------------------------------------------------------
# Capabilities handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseAppDecorator
from noc.inv.models.capability import Capability
from noc.sa.interfaces.base import (
    ListOfParameter,
    StringParameter,
    BooleanParameter,
    IntParameter,
)


class CapabilitiesHandlerDecorator(BaseAppDecorator):
    def contribute_to_class(self):
        self.add_view(
            "api_set_capabilities",
            self.api_set_capabilities,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/capabilities/(?P<capabilities_id>[0-9a-f]{24})/$",
            access="write",
            api=True,
            validate={"value": StringParameter() | IntParameter() | BooleanParameter()}
        )
        self.add_view(
            "api_reset_capabilities",
            self.api_reset_capabilities,
            method=["DELETE"],
            url=r"^(?P<object_id>[^/]+)/capabilities/(?P<capabilities_id>[0-9a-f]{24})/$",
            access="write",
            api=True,
        )

    def api_set_capabilities(self, request, object_id, capabilities_id, value):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        c = self.app.get_object_or_404(Capability, id=capabilities_id)
        o.set_caps(c.name, value)
        return {"status": True}

    def api_reset_capabilities(self, request, object_id, capabilities_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        c = self.app.get_object_or_404(Capability, id=capabilities_id)
        return {"status": True}


def capabilities_handler(cls):
    CapabilitiesHandlerDecorator(cls)
    return cls
