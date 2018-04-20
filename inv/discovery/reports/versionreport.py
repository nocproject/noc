## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Version inventory report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Report


class VersionReport(Report):
    system_notification = "sa.version_inventory"

    def __init__(self, job, enabled=True, to_save=False):
        super(VersionReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.changes = []

    def submit(self, data):
        """
        Submit version info:
        {
            'image': 'C2960-LANBASEK9-M',
            'platform': 'C2960',
            'vendor': 'Cisco',
            'version': '12.2(52)SE'
        }
        :param data: dict of versions
        :type data: dict
        :return:
        """
        if not self.enabled:
            return
        for k in data:
            v = data[k]
            ov = self.object.get_attr(k)
            if ov != v:
                self.changes += [(k, ov, v)]
                if self.to_save:
                    self.object.set_attr(k, v)
                self.info("%s: %s -> %s" % (k, ov, v))

    def send(self):
        if not self.enabled or not self.changes:
            return
        c = ["Version changes for %s:" % self.object.name]
        for name, old, new in self.changes:
            if old:
                c += ["    %s: %s -> %s" % (name, old, new)]
            else:
                c += ["    %s: %s (created)" % (name, new)]
        self.send_system_notification(
            "Version inventory changes for %s" % self.object.name,
            "\n".join(c))
