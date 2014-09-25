# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.probe application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import time
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.probe import Probe
from noc.pm.models.probeconfig import ProbeConfig
from noc.pm.models.metricsettings import MetricSettings
from noc.sa.interfaces.base import DateTimeParameter
from noc.settings import config


class ProbeApplication(ExtDocApplication):
    """
    PMProbe application
    """
    title = "Probe"
    menu = "Setup | Probes"
    model = Probe
    query_fields = ["name"]

    REFRESH_CHUNK = config.getint("pm", "expired_refresh_chunk")
    REFRESH_TIMEOUT = config.getint("pm", "expired_refresh_timeout")

    @view(url="^(?P<name>[^/]+)/(?P<instance>\d+)/config/$", method=["GET"],
          validate={
              "last": DateTimeParameter(required=False)
          },
          access="config", api=True)
    def api_config(self, request, name, instance, last=None):
        """
        Get full probe configuration
        """
        probe = self.get_object_or_404(Probe, name=name)
        if request.user.id != probe.user.id:
            return self.response_forbidden()
        instance = int(instance)
        if instance >= probe.n_instances:
            return self.response_not_found("Invalid instance")
        probe_id = str(probe.id)
        now = datetime.datetime.now()
        # Refresh expired congfigs
        t0 = time.time()
        nr = 0
        dt = 0
        for pc in ProbeConfig.objects.filter(probe_id=probe_id,
                                             instance_id=instance,
                                             expire__lt=now):
            pc.refresh()
            nr += 1
            if nr % self.REFRESH_CHUNK:
                # Check execution time
                dt = time.time() - t0
                if dt > self.REFRESH_TIMEOUT:
                    break
        if nr:
            self.logger.info(
                "%d configs has been refreshed in %s seconds. Giving up",
                nr, dt
            )
        # Get configs
        qs = ProbeConfig.objects.filter(probe_id=probe_id,
                                        instance_id=instance)
        if last:
            fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in last else "%Y-%m-%dT%H:%M:%S"
            last = datetime.datetime.strptime(last, fmt)
            qs = qs.filter(changed__gte=last)
        config = [{
            "uuid": pc.uuid,
            "handler": pc.handler,
            "interval": pc.interval,
            "metrics": [
                {
                    "metric": m.metric,
                    "metric_type": m.metric_type,
                    "thresholds": m.thresholds,
                    "convert": m.convert,
                    "scale": m.scale,
                    "collectors": {
                        "policy": m.collectors.policy,
                        "write_concern": m.collectors.write_concern,
                        "collectors": [
                            {
                                "proto": c.proto,
                                "address": c.address,
                                "port": c.port
                            } for c in m.collectors.collectors
                        ]
                    }
                } for m in pc.metrics
            ],
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
