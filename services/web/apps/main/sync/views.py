# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.sync application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import time
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.main.models.sync import Sync
from noc.main.models.synccache import SyncCache
from noc.sa.interfaces.base import DateTimeParameter
from noc.settings import config


class SyncApplication(ExtDocApplication):
    """
    Sync application
    """
    title = "Sync"
    menu = "Setup | Sync"
    glyph = "refresh"
    model = Sync
    query_fields = ["name"]

    REFRESH_CHUNK = config.getint("sync", "expired_refresh_chunk")
    REFRESH_TIMEOUT = config.getint("sync", "expired_refresh_timeout")

    @view(url="^(?P<name>[^/]+)/(?P<instance>\d+)/config/$", method=["GET"],
          validate={
              "last": DateTimeParameter(required=False)
          },
          access="config", api=True)
    def api_config(self, request, name, instance, last=None):
        """
        Get full probe configuration
        """
        sync = self.get_object_or_404(Sync, name=name)
        if request.user.id != sync.user.id:
            return self.response_forbidden()
        instance = int(instance)
        if instance >= sync.n_instances:
            return self.response_not_found("Invalid instance")
        sync_id = str(sync.id)
        now = datetime.datetime.now()
        # Refresh expired configs
        t0 = time.time()
        nr = 0
        dt = 0
        for sc in SyncCache.objects.filter(
                sync_id=sync_id,
                instance_id=instance,
                expire__lt=now
        ):
            sc.refresh()
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
        qs = SyncCache.objects.filter(
            sync_id=sync_id,
            instance_id=instance,
            expire__gt=now
        )
        if last:
            fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in last else "%Y-%m-%dT%H:%M:%S"
            last = datetime.datetime.strptime(last, fmt)
            qs = qs.filter(changed__gte=last)
        config = [{
            "uuid": sc.uuid,
            "type": sc.model_id,
            "data": sc.data,
            "changed": sc.changed.isoformat(),
            "expire": sc.expire.isoformat()
        } for sc in qs]
        if config:
            expire = min(c["expire"] for c in config)
            # Wipe out deleted configs
            deleted = [c["uuid"] for c in config if c["changed"] == c["expire"]]
            if deleted:
                SyncCache.objects.filter(uuid__in=deleted).delete()
        else:
            expire = None
        return {
            "now": now.isoformat(),
            "last": last.isoformat() if last else None,
            "expire": expire,
            "config": config
        }
