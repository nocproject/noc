# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ProbeConf API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import time
## NOC modules
from noc.lib.service.api.base import API, api
from noc.pm.models.probeconfig import ProbeConfig


class ProbeConfAPI(API):
    """
    PM collector api
    """
    name = "probeconf"

    REFRESH_CHUNK = 100
    REFRESH_TIMEOUT = 100

    @api
    def get_config(self, last=None):
        pool = self.service.config.pool
        now = datetime.datetime.now()
        # Refresh expired configs
        t0 = time.time()
        nr = 0
        dt = 0
        stopped = False
        for pc in ProbeConfig.objects.filter(pool=pool,
                                             expire__lt=now):
            pc.refresh()
            nr += 1
            if nr % self.REFRESH_CHUNK:
                # Check execution time
                dt = time.time() - t0
                if dt > self.REFRESH_TIMEOUT:
                    self.service.logger.info(
                        "%d configs has been refreshed in %s seconds. Giving up",
                        nr, dt
                    )
                    stopped = True
                    break
        if nr and not stopped:
            self.service.logger.info(
                "%d configs has been refreshed in %s seconds.",
                nr, dt
            )
        # Get configs
        q = {
            "pool": pool,
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
                    "scale": m["scale"]
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
