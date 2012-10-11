## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Version inventory job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.settings import config
from base import MODiscoveryJob
from noc.inv.discovery.reports.versionreport import VersionReport


class VersionInventoryJob(MODiscoveryJob):
    name = "version_inventory"
    map_task = "get_version"
    system_notification = "sa.version_inventory"

    ignored = not config.getboolean("version_inventory", "enabled")
    initial_submit_interval = config.getint("version_inventory",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("version_inventory",
        "initial_submit_concurrency")
    to_save = config.getboolean("version_inventory", "save")

    def handler(self, object, result):
        r = {}
        for k in result:
            v = result[k]
            if k == "attributes":
                for kk in v:
                    r[kk] = v[kk]
            else:
                r[k] = v
        self.report = VersionReport(self, to_save=self.to_save)
        self.report.submit(r)
        self.report.send()
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_version_inventory": True}

    def can_run(self):
        return (super(VersionInventoryJob, self).can_run()
                and self.object.object_profile.enable_version_inventory)

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.version_inventory_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.version_inventory_min_interval
