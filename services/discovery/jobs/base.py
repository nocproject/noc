#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic MO discovery job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject

    def __init__(self, *args, **kwargs):
        super(MODiscoveryJob, self).__init__(*args, **kwargs)
        self.if_cache = {}

    def can_run(self):
        return self.object.is_managed

    def update_if_changed(self, obj, values, ignore_empty=None):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :param ignore_empty: List of fields which may be ignored if empty
        :returns: List of changed (key, value)
        :rtype: list
        """
        changes = []
        ignore_empty = ignore_empty or []
        for k, v in values.items():
            vv = getattr(obj, k)
            if v != vv:
                if type(v) != int or not hasattr(vv, "id") or v != vv.id:
                    if k in ignore_empty and (v is None or v == ""):
                        continue
                    setattr(obj, k, v)
                    changes += [(k, v)]
        if changes:
            obj.save()
        return changes

    def log_changes(self, msg, changes):
        """
        Log changes
        :param msg: Message
        :type msg: str
        """
        if changes:
            self.logger.info("%s: %s" % (
                msg, ", ".join("%s = %s" % (k, v) for k, v in changes)))

    def get_interface(self, name):
        """
        Returns Interface instance
        """
        if name not in self.if_cache:
            i = Interface.objects.filter(
                managed_object=self.object.id,
                name=name
            ).first()
            self.if_cache[name] = i
        return self.if_cache[name]
