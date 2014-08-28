# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.probe application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.probe import Probe
from noc.pm.models.probeconfig import ProbeConfig
from noc.pm.models.metricsettings import MetricSettings


class ProbeApplication(ExtDocApplication):
    """
    PMProbe application
    """
    title = "Probe"
    menu = "Setup | Probes"
    model = Probe
    query_fields = ["name"]

    @view(url="^(?P<name>[^/]+)/config/$", method=["GET"],
          access="config", api=True)
    def api_config(self, request, name):
        """
        Get full probe configuration
        """
        probe = self.get_object_or_404(Probe, name=name)
        probe_id = str(probe.id)
        now = datetime.datetime.now()
        expired = set(
            ProbeConfig.objects.filter(
                probe_id=probe_id, expired__lt=now)
            .only("model_id", "object_id")
            .values_list("model_id", "object_id")
        )
        # Rebuild expired configs
        for model_id, object_id in expired:
            object = MetricSettings(model_id=model_id, object_id=object_id).get_object()
            ProbeConfig.refresh_object(object)
        # Get configs
        config = [{
            "uuid": pc.uuid,
            "metric": pc.metric,
            "metric_type": pc.metric_type,
            "handler": pc.handler,
            "interval": pc.interval,
            "thresholds": pc.thresholds,
            "config": pc.config,
            "expired": pc.expired.isoformat()
        } for pc in ProbeConfig.objects.filter(probe_id=probe_id)]
        return {
            "config": config
        }