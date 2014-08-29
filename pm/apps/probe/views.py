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
from noc.sa.interfaces.base import DateTimeParameter


class ProbeApplication(ExtDocApplication):
    """
    PMProbe application
    """
    title = "Probe"
    menu = "Setup | Probes"
    model = Probe
    query_fields = ["name"]

    @view(url="^(?P<name>[^/]+)/config/$", method=["GET"],
          validate={
              "last": DateTimeParameter(required=False)
          },
          access="config", api=True)
    def api_config(self, request, name, last=None):
        """
        Get full probe configuration
        """

        probe = self.get_object_or_404(Probe, name=name)
        if request.user.id != probe.user.id:
            return self.response_forbidden()
        probe_id = str(probe.id)
        now = datetime.datetime.now()
        # Refresh expired congfigs
        expired = set(
            ProbeConfig.objects.filter(
                probe_id=probe_id,
                expire__lt=now
            )
            .only("model_id", "object_id")
            .values_list("model_id", "object_id")
        )
        # Rebuild expired configs
        for model_id, object_id in expired:
            object = MetricSettings(
                model_id=model_id, object_id=object_id).get_object()
            ProbeConfig.refresh_object(object)
        # Get configs
        qs = ProbeConfig.objects.filter(probe_id=probe_id)
        if last:
            last = datetime.datetime.strptime(last,
                                              "%Y-%m-%dT%H:%M:%S.%f")
            qs = qs.filter(changed__gte=last)
        config = [{
            "uuid": pc.uuid,
            "metric": pc.metric,
            "metric_type": pc.metric_type,
            "handler": pc.handler,
            "interval": pc.interval,
            "thresholds": pc.thresholds,
            "config": pc.config,
            "changed": pc.changed.isoformat(),
            "expire": pc.expire.isoformat()
        } for pc in qs]
        if config:
            expire = min(c["expire"] for c in config)
            # Wipe out deleted configs
            deleted = [c["uuid"] for c in config if c["changed"] == c["expire"]]
            if deleted:
                ProbeConfig.objects.filter(uuid__in=deleted).delete()
        else:
            expire = None
        return {
            "now": now.isoformat(),
            "last": last.isoformat() if last else None,
            "expire": expire,
            "config": config
        }