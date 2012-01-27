# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.overlay application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.gis.models import Overlay
from noc.gis.geo import inverse_mercator


class OverlayApplication(ExtDocApplication):
    """
    Overlay application
    """
    title = "Overlay"
    menu = "Setup | Overlays"
    model = Overlay

    def extra_permissions(self):
        x = set([s.permission_name
                 for s in
                 Overlay.objects.all()])
        return list(x)

    @view(url="^gate/(?P<gate_id>[a-zA-Z0-9_\-]+)/$", method=["GET"],
          access="launch", api=True)
    def api_gate(self, request, gate_id):
        # Find overlay
        overlay = Overlay.objects.filter(gate_id=gate_id).first()
        if overlay is None:
            return self.response_not_found("Gate not found")
        if not overlay.is_active:
            return self.rensponse_not_found("Overlay is disabled")
        # Parse bbox
        kwargs = dict(request.GET.items())
        if "bbox" in kwargs:
            bbox = kwargs["bbox"]
            bbox = [float(x) for x in bbox.split(",")]
            # Reproject from EPSG:900913 to EPSG:4326
            bbox = [
                inverse_mercator([bbox[0], bbox[1]]),
                inverse_mercator([bbox[2], bbox[3]])
            ]
            kwargs["bbox"] = bbox
        # Build overlay
        o = overlay.get_overlay()
        return o.handle(**kwargs)
