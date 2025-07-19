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
    StringParameter,
    BooleanParameter,
    IntParameter,
    StringListParameter,
)


class CapabilitiesHandlerDecorator(BaseAppDecorator):
    def contribute_to_class(self):
        self.add_view(
            "api_set_capabilities",
            self.api_set_capabilities,
            method=["PUT"],
            url=r"^(?P<object_id>[^/]+)/capabilities/(?P<capabilities_id>[0-9a-f]{24})/$",
            access="write",
            api=True,
            validate={
                "value": StringListParameter(strict=True)
                | StringParameter()
                | IntParameter()
                | BooleanParameter()
            },
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
        capability = self.app.get_object_or_404(Capability, id=capabilities_id)
        if not capability.allow_manual:
            return self.app.render_json(
                {"status": False, "message": "Not allowed manual edit"}, status=403
            )
        try:
            o.set_caps(capability.name, value)
        except ValueError as e:
            return self.app.render_json(
                {"status": False, "message": str(e)}, status=self.app.BAD_REQUEST
            )
        return {
            "status": True,
            "data": {
                "capability": capability.name,
                "id": str(capability.id),
                "object": str(o.id),
                "description": capability.description,
                "type": capability.type.value,
                "value": value,
                "source": "manual",
                "scope": "",
                "editor": capability.get_editor(),
            },
        }

    def api_reset_capabilities(self, request, object_id, capabilities_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        capability = self.app.get_object_or_404(Capability, id=capabilities_id)
        if not capability.allow_manual:
            return self.app.render_json(
                {"status": False, "message": "Not allowed manual edit"}, status=403
            )
        o.reset_caps(capability.name)
        return {"status": True}


def capabilities_handler(cls):
    CapabilitiesHandlerDecorator(cls)
    return cls
