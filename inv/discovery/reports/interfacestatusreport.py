## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Status Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Report
from noc.inv.models.interface import Interface


class InterfaceStatusReport(Report):
    system_notification = "sa.version_inventory"

    def __init__(self, job, enabled=True, to_save=False):
        super(InterfaceStatusReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.interfaces = dict(
            (i.name, i)
            for i in Interface.objects.filter(managed_object=job.key)
        )

    def submit(self, interface, **kwargs):
        if not self.enabled:
            return
        iface = self.interfaces.get(interface)
        if not iface:
            return
        changes = self.update_if_changed(
            iface, kwargs,
            ignore_empty=kwargs.keys()
        )
        self.log_changes(
            "Interface %s status has been changed" % interface,
            changes
        )

    def send(self):
        pass
