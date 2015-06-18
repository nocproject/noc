## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic Managed Object-based discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.interface import Interface
from noc.lib.scheduler.intervaljob import IntervalJob


class MODiscoveryJob(IntervalJob):
    ignored = True

    def get_display_key(self):
        if self.object:
            return self.object.name
        else:
            return self.key

    @classmethod
    def can_submit(cls, object):
        """
        Check object is submittable
        :param cls:
        :param object:
        :return:
        """
        return True

    def get_defererence_query(self):
        """
        Restrict job to objects having *is_managed* set
        :return:
        """
        return {"id": self.key, "is_managed": True}

    def can_run(self):
        if self.map_task:
            if not self.object.is_managed:
                self.logger.debug("Object is not managed")
                return False
            if not self.object.get_status():
                self.logger.debug("Object is down")
                return False
        return True

    def get_group(self):
        return "discovery-%s" % self.key

    def get_interface_by_name(self, object, name):
        """
        Find interface by name
        :param object: Managed Object
        :param name: interface name
        :return: Interface instance or None
        """
        i = Interface.objects.filter(
            managed_object=object.id, name=name).first()
        if i:
            return i
        # Construct alternative names
        alt_names = object.profile.get_interface_names(name)
        nn = object.profile.convert_interface_name(name)
        if nn != name:
            alt_names = [nn] + alt_names
        for n in alt_names:
            i = Interface.objects.filter(
                managed_object=object.id, name=n).first()
            if i:
                return i
        return None
