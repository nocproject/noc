# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## One-time job to sync permissions
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job
from noc.main.models.permission import Permission


class SyncPermissionsJob(Job):
    name = "main.sync_permissions"
    threaded = True
    ignored = False

    def handler(self, *args, **kwargs):
        Permission.sync()
        return True
