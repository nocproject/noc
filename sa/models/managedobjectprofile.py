# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectProfile
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
## NOC modules
from noc.main.models.style import Style
from noc.lib.validators import is_fqdn
from noc.lib.stencil import stencil_registry
from noc.pm.models.probeconfig import probe_config
from noc.core.model.fields import TagsField


@probe_config
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
    level = models.IntegerField(_("Level"), default=25)
    style = models.ForeignKey(
        Style, verbose_name=_("Style"), blank=True, null=True)
    # Stencils
    shape = models.CharField(_("Shape"), blank=True, null=True,
        choices=stencil_registry.choices, max_length=128)
    ## Name restrictions
    # Regular expression to check name format
    name_template = models.CharField(_("Name template"), max_length=256,
        blank=True, null=True)
    ## IPAM Synchronization
    ## During ManagedObject save
    sync_ipam = models.BooleanField(_("Sync. IPAM"), default=False)
    fqdn_template = models.TextField(_("FQDN template"),
        null=True, blank=True)
    #@todo: Name validation function
    ## FM settings
    enable_ping = models.BooleanField(
        _("Enable ping check"), default=True)
    ping_interval = models.IntegerField(_("Ping interval"), default=60)
    # Host down alarm severity
    # Default impact is MAJOR/4000
    down_severity = models.IntegerField(
        _("Down severity"), default=4000)
    # check_link alarm job interval settings
    # Either None or T0,I0,T1,I1,...,Tn-1,In-1,,In
    # See MultiIntervalJob settings for details
    check_link_interval = models.CharField(
        _("check_link interval"),
        max_length=256, blank=True, null=True,
        default=",60"
    )
    # Enable box discovery.
    # Box discovery launched on system changes
    enable_box_discovery = models.BooleanField(default=True)
    # Interval of periodic discovery when no changes registered
    box_discovery_interval = models.IntegerField(default=86400)
    # Retry interval in case of failure (Object is down)
    box_discovery_failed_interval = models.IntegerField(default=10800)
    # Start box discovery when system start registered
    box_discovery_on_system_start = models.BooleanField(default=False)
    # after delay
    box_discovery_system_start_delay = models.IntegerField(default=300)
    # Start box discovery when config change registered
    box_discovery_on_config_changed = models.BooleanField(default=False)
    # After delay
    box_discovery_config_changed_delay = models.IntegerField(default=300)
    # Check profile
    enable_box_discovery_profile = models.BooleanField(default=True)
    # Collect version info
    enable_box_discovery_version = models.BooleanField(default=False)
    # Collect capabilities
    enable_box_discovery_caps = models.BooleanField(default=False)
    # Collect interface settings
    enable_box_discovery_interface = models.BooleanField(default=False)
    # Extract interface prefixes and synchronize with ipam
    enable_box_discovery_prefix = models.BooleanField(default=False)
    # Collect chassis ID information
    enable_box_discovery_id = models.BooleanField(default=False)
    # Collect config
    enable_box_discovery_config = models.BooleanField(default=False)
    # Collect hardware configuration
    enable_box_discovery_asset = models.BooleanField(default=False)
    # Collect interface IP addresses
    # enable_box_discovery_ip = models.BooleanField(default=False)
    # Collect static vlans
    enable_box_discovery_vlan = models.BooleanField(default=False)
    # L2 topology using BFD
    enable_box_discovery_bfd = models.BooleanField(default=False)
    # L2 topology using CDP
    enable_box_discovery_cdp = models.BooleanField(default=False)
    # L2 topology using FDP
    enable_box_discovery_fdp = models.BooleanField(default=False)
    # L2 topology using LLDP
    enable_box_discovery_lldp = models.BooleanField(default=False)
    # L2 topology using OAM
    enable_box_discovery_oam = models.BooleanField(default=False)
    # L2 topology using REP
    enable_box_discovery_rep = models.BooleanField(default=False)
    # L2 topology using STP
    enable_box_discovery_stp = models.BooleanField(default=False)
    # L2 topology using UDLD
    enable_box_discovery_udld = models.BooleanField(default=False)
    # Enable periodic discovery.
    # Periodic discovery launched repeatedly
    enable_periodic_discovery = models.BooleanField(default=True)
    # Periodic discovery repeat interval
    periodic_discovery_interval = models.IntegerField(default=300)
    # Collect uptime
    enable_periodic_discovery_uptime = models.BooleanField(default=False)
    # Collect interface status
    enable_periodic_discovery_interface_status = models.BooleanField(default=False)
    # Collect mac address table
    enable_periodic_discovery_mac = models.BooleanField(default=False)
    # Collect ARP cache
    # enable_periodic_discovery_ip = models.BooleanField(default=False)
    tags = TagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_fqdn(self, object):
        if self.fqdn_template:
            # Render template
            ctx = Context({"object": object})
            f = Template(self.fqdn_template).render(ctx)
            # Remove spaces
            f = "".join(f.split())
        else:
            f = object.name
        # Check resulting fqdn
        if not is_fqdn(f):
            raise ValueError("Invalid FQDN: %s" % f)
        return f

    def get_probe_config(self, config):
        raise ValueError("Invalid config parameter '%s'" % config)
