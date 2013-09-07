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
from django.template import Template, Context
## NOC modules
from noc.main.models.style import Style
from noc.lib.validators import is_fqdn
from noc.lib.stencil import stencil_registry


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
    # Stencils
    shape = models.CharField(_("Shape"), blank=True, null=True,
        choices=stencil_registry.choices, max_length=128)
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
    ping_interval = models.IntegerField(_("Ping interval"), default=60)
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
    # VLAN discovery
    enable_vlan_discovery = models.BooleanField(
        _("Enable VLAN discovery"), default=False)
    vlan_discovery_min_interval = models.IntegerField(
        _("Min. VLAN discovery interval"), default=600)
    vlan_discovery_max_interval = models.IntegerField(
        _("Max. VLAN discovery interval"), default=86400)
    # MAC discovery
    enable_mac_discovery = models.BooleanField(
            _("Enable MAC discovery"), default=True)
    mac_discovery_min_interval = models.IntegerField(
        _("Min. MAC discovery interval"), default=600)
    mac_discovery_max_interval = models.IntegerField(
        _("Max. MAC discovery interval"), default=86400)
    # ID Discovery
    enable_id_discovery = models.BooleanField(
            _("Enable ID discovery"), default=True)
    id_discovery_min_interval = models.IntegerField(
        _("Min. ID discovery interval"), default=600)
    id_discovery_max_interval = models.IntegerField(
        _("Max. ID discovery interval"), default=86400)
    # LLDP Topology discovery
    enable_lldp_discovery = models.BooleanField(
            _("Enable LLDP discovery"), default=True)
    lldp_discovery_min_interval = models.IntegerField(
        _("Min. LLDP discovery interval"), default=600)
    lldp_discovery_max_interval = models.IntegerField(
        _("Max. LLDP discovery interval"), default=86400)
    # CDP Topology discovery
    enable_cdp_discovery = models.BooleanField(
            _("Enable CDP discovery"), default=True)
    cdp_discovery_min_interval = models.IntegerField(
        _("Min. CDP discovery interval"), default=600)
    cdp_discovery_max_interval = models.IntegerField(
        _("Max. CDP discovery interval"), default=86400)
    # FDP Topology discovery
    enable_fdp_discovery = models.BooleanField(
            _("Enable FDP discovery"), default=True)
    fdp_discovery_min_interval = models.IntegerField(
        _("Min. FDP discovery interval"), default=600)
    fdp_discovery_max_interval = models.IntegerField(
        _("Max. FDP discovery interval"), default=86400)
    # STP Topology discovery
    enable_stp_discovery = models.BooleanField(
            _("Enable STP discovery"), default=True)
    stp_discovery_min_interval = models.IntegerField(
        _("Min. STP discovery interval"), default=600)
    stp_discovery_max_interval = models.IntegerField(
        _("Max. STP discovery interval"), default=86400)
    # REP Topology discovery
    enable_rep_discovery = models.BooleanField(
            _("Enable REP discovery"), default=True)
    rep_discovery_min_interval = models.IntegerField(
        _("Min. REP discovery interval"), default=600)
    rep_discovery_max_interval = models.IntegerField(
        _("Max. REP discovery interval"), default=86400)
    # BFD Topology discovery
    enable_bfd_discovery = models.BooleanField(
            _("Enable BFD discovery"), default=True)
    bfd_discovery_min_interval = models.IntegerField(
        _("Min. BFD discovery interval"), default=600)
    bfd_discovery_max_interval = models.IntegerField(
        _("Max. BFD discovery interval"), default=86400)
    # UDLD Topology discovery
    enable_udld_discovery = models.BooleanField(
            _("Enable UDLD discovery"), default=True)
    udld_discovery_min_interval = models.IntegerField(
        _("Min. UDLD discovery interval"), default=600)
    udld_discovery_max_interval = models.IntegerField(
        _("Max. UDLD discovery interval"), default=86400)
    # OAM Topology discovery
    enable_oam_discovery = models.BooleanField(
            _("Enable UDLD discovery"), default=True)
    oam_discovery_min_interval = models.IntegerField(
        _("Min. OAM discovery interval"), default=600)
    oam_discovery_max_interval = models.IntegerField(
        _("Max. OAM discovery interval"), default=86400)

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
