# ----------------------------------------------------------------------
# Sync Purgatorium Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.sa.models.discoveredobject import sync_purgatorium
from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule


class SyncPurgatoriumJob(PeriodicJob):
    def handler(self, **kwargs):
        sync_purgatorium()

    def can_run(self):
        return bool(ObjectDiscoveryRule.objects.filter(is_active=True).first())

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return 60
