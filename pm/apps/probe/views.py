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
import itertools
import struct
## Third-party modules
from bson.binary import Binary
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.probe import Probe
from noc.pm.models.probeconfig import ProbeConfig
from noc.sa.interfaces.base import (
    DictListParameter, StringParameter,
    FloatParameter, DateTimeParameter, IntParameter)
from noc.settings import config
from noc.fm.models.newevent import NewEvent


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
        if not probe.user or request.user.id != probe.user.id:
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
        stopped = False
        for pc in ProbeConfig.objects.filter(probe_id=probe_id,
                                             instance_id=instance,
                                             expire__lt=now):
            pc.refresh()
            nr += 1
            if nr % self.REFRESH_CHUNK:
                # Check execution time
                dt = time.time() - t0
                if dt > self.REFRESH_TIMEOUT:
                    self.logger.info(
                        "%d configs has been refreshed in %s seconds. Giving up",
                        nr, dt
                    )
                    stopped = True
                    break
        if nr and not stopped:
            self.logger.info(
                "%d configs has been refreshed in %s seconds.",
                nr, dt
            )
        # Get configs
        q = {
            "probe_id": probe_id,
            "instance_id": instance
        }
        if last:
            fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in last else "%Y-%m-%dT%H:%M:%S"
            last = datetime.datetime.strptime(last, fmt)
            q["changed"] = {"$gte": last}
        config = [{
            "uuid": pc["uuid"],
            "handler": pc["handler"],
            "interval": pc["interval"],
            "metrics": [
                {
                    "metric": m["metric"],
                    "metric_type": m["metric_type"],
                    "thresholds": m["thresholds"],
                    "convert": m["convert"],
                    "scale": m["scale"],
                    "collectors": {
                        "policy": m["collectors"]["policy"],
                        "write_concern": m["collectors"]["write_concern"],
                        "collectors": [
                            {
                                "proto": c["proto"],
                                "address": c["address"],
                                "port": c["port"]
                            } for c in m["collectors"]["collectors"]
                        ]
                    }
                } for m in pc["metrics"]
            ],
            "config": pc["config"],
            "managed_object": pc.get("managed_object", None),
            "changed": pc["changed"].isoformat(),
            "expire": pc["expire"].isoformat()
        } for pc in ProbeConfig._get_collection().find(q)]
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

    @view(url="^(?P<name>[^/]+)/(?P<instance>\d+)/feed/$",
          method=["POST"],
          validate={
              "thresholds": DictListParameter(attrs={
                "managed_object": IntParameter(),
                "metric": StringParameter(),
                "metric_type": StringParameter(),
                "ts": IntParameter(),
                "value": FloatParameter(),
                "old_state": StringParameter(),
                "new_state": StringParameter()
              })
          },
          access="config", api=True)
    def api_fmfeed(self, request, name, instance, thresholds):
        if thresholds:
            cnt = itertools.count()
            batch = NewEvent._get_collection().initialize_unordered_bulk_op()
            for t in thresholds:
                seq = struct.pack(
                    "!II",
                    int(time.time()),
                    cnt.next() & 0xFFFFFFFFL
                )
                batch.insert({
                    "timestamp": datetime.datetime.fromtimestamp(t["ts"]),
                    "managed_object": t["managed_object"],
                    "raw_vars": {
                        "source": "system",
                        "metric": t["metric"],
                        "metric_type": t["metric_type"],
                        "value": str(t["value"]),
                        "old_state": t["old_state"],
                        "new_state": t["new_state"]
                    },
                    "seq": Binary(seq)
                })
            batch.execute(0)
