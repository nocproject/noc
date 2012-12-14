# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectProfile
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.main.models.style import Style


class ManagedObjectProfile(models.Model):

    class Meta:
        verbose_name = _("Managed Object Profile")
        verbose_name_plural = _("Managed Object Profiles")
        db_table = "sa_managedobjectprofile"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(
        _("Description"), blank=True, null=True)
    style = models.ForeignKey(
        Style, verbose_name=_("Style"), blank=True, null=True)
    ## Name restrictions
    # Regular expression to check name format
    name_template = models.CharField(_("Name template"), max_length=256,
        blank=True, null=True)
    ## IPAM Synchronization
    sync_ipam = models.BooleanField(_("Sync. IPAM"), default=False)
    fqdn_template = models.TextField(_("FQDN template"),
        null=True, blank=True)
    #@todo: Name validation function
    ## FM settings
    enable_ping = models.BooleanField(
        _("Enable ping check"), default=True)
    # Host down alarm severity
    # Default impact is MAJOR/4000
    down_severity = models.IntegerField(
        _("Down severity"), default=4000)
    ## Config polling
    enable_config_polling  = models.BooleanField(
        _("Enable config polling"), default=True)
    config_polling_min_interval = models.IntegerField(
        _("Min. config polling interval"), default=600)
    config_polling_max_interval = models.IntegerField(
        _("Max. config polling interval"), default=86400)
    ## Discovery settings
    # Version inventory
    enable_version_inventory = models.BooleanField(
        _("Enable version inventory"), default=True)
    version_inventory_min_interval = models.IntegerField(
        _("Min. version inventory interval"), default=600)
    version_inventory_max_interval = models.IntegerField(
        _("Max. version inventory interval"), default=86400)
    # Interface discovery
    enable_interface_discovery = models.BooleanField(
        _("Enable interface discovery"), default=True)
    interface_discovery_min_interval = models.IntegerField(
        _("Min. interface discovery interval"), default=600)
    interface_discovery_max_interval = models.IntegerField(
        _("Max. interface discovery interval"), default=86400)
    # IP discovery
    enable_ip_discovery = models.BooleanField(
        _("Enable IP discovery"), default=True)
    ip_discovery_min_interval = models.IntegerField(
        _("Min. IP discovery interval"), default=600)
    ip_discovery_max_interval = models.IntegerField(
        _("Max. IP discovery interval"), default=86400)
    # Prefix discovery
    enable_prefix_discovery = models.BooleanField(
        _("Enable prefix discovery"), default=True)
    prefix_discovery_min_interval = models.IntegerField(
        _("Min. prefix discovery interval"), default=600)
    prefix_discovery_max_interval = models.IntegerField(
        _("Max. prefix discovery interval"), default=86400)
    # MAC discovery
    enable_mac_discovery = models.BooleanField(
            _("Enable MAC discovery"), default=True)
    mac_discovery_min_interval = models.IntegerField(
        _("Min. MAC discovery interval"), default=600)
    mac_discovery_max_interval = models.IntegerField(
        _("Max. MAC discovery interval"), default=86400)
    # Topology discovery
    # enable_topology_discovery = models.BooleanField(
    #        _("Enable topology discovery"), default=True)

    def __unicode__(self):
        return self.name
