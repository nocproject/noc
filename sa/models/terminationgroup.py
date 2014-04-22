# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BRASGroup
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules


class TerminationGroup(models.Model):
    """
    Termination Group
    """
    class Meta:
        verbose_name = "Termination Group"
        verbose_name_plural = "Termination Groups"
        db_table = "sa_terminationgroup"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)
    # Dynamic pools oversubscription, in persent
    # 0 - no oversub
    # 10 -- 10% oversubscription
    # -10  -- Reserve 10%
    # dynamic_oversub = models.IntegerField("Dynamic Oversub", default=0)

    def __unicode__(self):
        return self.name

    def _check_technology(self, name):
        from noc.inv.models.technology import Technology
        if not Technology.objects.filter(name="Packet | %s" % name).count():
            raise ValueError("Invalid technology: '%s'" % name)

    def register_dynamic_usage(self, vrf=None, name="default",
                               technology="IPoE"):
        """
        Increase dynamic pool usage
        """
        ## Avoid circular references
        from noc.ip.models.vrf import VRF
        from noc.ip.models.dynamicippoolusage import DynamicIPPoolUsage

        self._check_technology(technology)
        if not vrf:
            vrf = VRF.get_global()
        DynamicIPPoolUsage.register_usage(self, vrf, name, technology)

    def unregister_dynamic_usage(self, vrf=None, name="default",
                                 technology="IPoE"):
        """
        Decrease dynamic pool usage
        """
        ## Avoid circular references
        from noc.ip.models.vrf import VRF
        from noc.ip.models.dynamicippoolusage import DynamicIPPoolUsage

        self._check_technology(technology)
        if not vrf:
            vrf = VRF.get_global()
        DynamicIPPoolUsage.unregister_usage(self, vrf, name, technology)

    @property
    def dynamic_usage(self):
        """
        Retuns dict of dynamic pool name -> technology -> usage counter
        """
        ## Avoid circular references
        from noc.ip.models.vrf import VRF
        from noc.ip.models.dynamicippoolusage import DynamicIPPoolUsage

        usage = {}
        for p in self.ippool_set.filter(type="D"):
            if p.name not in usage:
                usage[p.name] = {}
                for t in p.technologies:
                    usage[p.name][t] = DynamicIPPoolUsage.get_usage(
                        self, p.vrf, p.name, t)
        return usage
