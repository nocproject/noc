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
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.lib.debug import error_report
from noc.lib.log import PrefixLoggerAdapter


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject

    def can_run(self):
        return self.object.is_managed


class DiscoveryCheck(object):
    name = None
    # If not none, check required script is available
    # before running check
    required_script = None

    def __init__(self, job):
        self.job = job
        self.object = self.job.object
        self.logger = PrefixLoggerAdapter(
            self.job.logger.logger,
            "%s][%s][%s" % (self.job.name, self.name, self.object.name)
        )
        self.if_cache = {}
        self.sub_cache = {}
        self.profile_cache = {}

    def run(self):
        if (self.required_script and
                self.required_script not in self.object.scripts):
            self.logger.info("%s script is not supported. Skipping",
                             self.required_script)
            return
        try:
            self.handler()
        except Exception:
            error_report()

    def handler(self):
        pass

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

    def set_interface(self, name, iface):
        """
        Fill interface cache
        """
        self.if_cache[name] = iface

    def get_subinterface(self, interface, name):
        """
        Returns Interface instance
        """
        key = (str(interface.id), name)
        if key not in self.sub_cache:
            si = SubInterface.objects.filter(
                interface=interface.id, name=name).first()
            self.sub_cache[key] = si
        return self.sub_cache[key]

    def get_interface_profile(self, name):
        if name not in self.profile_cache:
            p = InterfaceProfile.objects.filter(name=name).first()
            self.profile_cache[name] = p
        return self.profile_cache[name]
