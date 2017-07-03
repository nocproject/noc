# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BRASGroup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Django modules
from django.db import models
# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.fields import TagsField, DocumentReferenceField
from noc.core.model.decorator import on_delete_check


@on_delete_check(check=[
    # ("ip.DynamicIPPoolUsage", "termination_group"),
    ("sa.ManagedObject", "termination_group"),
    ("sa.ManagedObject", "service_terminator"),
    ("sa.ManagedObjectSelector", "filter_termination_group"),
    ("sa.ManagedObjectSelector", "filter_service_terminator")
])
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

    # Integration with external NRI systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem,
                                           null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(null=True, blank=True)

    tags = TagsField("Tags", null=True, blank=True)

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
        # Avoid circular references
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
        # Avoid circular references
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
        # Avoid circular references
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
