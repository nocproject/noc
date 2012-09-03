## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Version inventory job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.sa.models.managedobject import ManagedObject


class VersionInventoryJob(IntervalJob):
    name = "version_inventory"
    map_task = "get_version"
    system_notification = "sa.version_inventory"

    initial_submit_interval = 300  # @todo: Config
    success_retry = 86400
    failed_retry = 600

    @classmethod
    def initial_submit(cls, scheduler, keys):
        for mo in ManagedObject.objects.filter(
            is_managed=True).exclude(id__in=keys).only("id"):
            cls.submit(
                scheduler=scheduler, key=mo.id,
                interval=cls.success_retry, randomize=True)

    def get_defererence_query(self):
        """
        Restrict job to objects having *is_managed* set
        :return:
        """
        return {"id": self.key, "is_managed": True}

    def handler(self, object, result):
        c = []  # name, old, new
        for k,v in result.items():
            if k == "attributes":
                for kk, vv in v.items():
                    ov = object.get_attr(kk)
                    if ov != vv:
                        object.set_attr(kk, vv)
                        c += [(kk, ov, vv)]
            else:
                ov = object.get_attr(k)
                if ov != v:
                    object.set_attr(k, v)
                    c += [(k, ov, v)]
        if c:
            changes = ["Version changes for %s:" % object.name]
            for name, old, new in c:
                if old:
                    changes += ["    %s: %s -> %s" % (name, old, new)]
                else:
                    changes += ["    %s: %s (created)" % (name, new)]
            self.notify(
                "Version inventory changes for %s" % object.name,
                "\n".join(changes))
        return True
