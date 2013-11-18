## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Asset Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.settings import config
from noc.inv.discovery.reports.asset import AssetReport
from noc.lib.text import str_dict


class AssetDiscoveryJob(MODiscoveryJob):
    """
    AssetDiscovery
    """
    name = "asset_discovery"
    map_task = "get_inventory"
    ignored = not config.getboolean("asset_discovery", "enabled")
    initial_submit_interval = config.getint("asset_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("asset_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("asset_discovery", "save")

    def handler(self, object, result):
        self.report = AssetReport(self, to_save=self.to_save)
        #
        self.report.find_managed()
        # Submit objects
        for o in result:
            self.debug("Submit %s" % str_dict(o))
            self.report.submit(
                type=o["type"], number=o.get("number"),
                builtin=o["builtin"],
                vendor=o.get("vendor"), part_no=o["part_no"],
                revision=o.get("revision"), serial=o.get("serial"),
                description=o.get("description")
            )
        # Assign stack members
        self.report.submit_stack_members()
        #
        self.report.submit_connections()
        #
        self.report.check_management()
        # Finish
        self.report.send()
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_asset_discovery": True}

    def can_run(self):
        return (super(AssetDiscoveryJob, self).can_run()
                and getattr(self.object.object_profile,
                    "enable_asset_discovery"))

    @classmethod
    def get_submit_interval(cls, object):
        return getattr(object.object_profile,
            "asset_discovery_max_interval")

    def get_failed_interval(self):
        return getattr(self.object.object_profile,
            "asset_discovery_min_interval")
