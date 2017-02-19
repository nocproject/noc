# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectProfile
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
from threading import Lock
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
import cachetools
## NOC modules
from noc.main.models.style import Style
from authprofile import AuthProfile
from noc.lib.validators import is_fqdn
from noc.lib.stencil import stencil_registry
from noc.core.model.fields import TagsField, PickledField
from noc.core.model.decorator import on_save, on_init, on_delete_check
from noc.main.models.pool import Pool
from noc.core.scheduler.job import Job
from noc.core.defer import call_later
from objectmap import ObjectMap

id_lock = Lock()


@on_init
@on_save
@on_delete_check(check=[
    ("sa.ManagedObject", "object_profile"),
    ("sa.ManagedObjectProfile", "cpe_profile"),
    ("sa.ManagedObjectSelector", "filter_object_profile"),
    ("inv.FirmwarePolicy", "object_profile")
])
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
    report_ping_rtt = models.BooleanField(
        _("Report RTT"),
        default=False
    )
    # Additional alarm weight
    weight = models.IntegerField(
        "Alarm weight",
        default=0
    )
    #
    card = models.CharField(
        _("Card name"),
        max_length=256, blank=True, null=True,
        default="managedobject"
    )
    card_title_template = models.CharField(
        _("Card title template"),
        max_length=256,
        default="{{ object.object_profile.name }}: {{ object.name }}"
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
    # Collect hardware configuration
    enable_box_discovery_nri = models.BooleanField(default=False)
    # Collect interface IP addresses
    # enable_box_discovery_ip = models.BooleanField(default=False)
    # Collect static vlans
    enable_box_discovery_vlan = models.BooleanField(default=False)
    # L2 topology using BFD
    enable_box_discovery_bfd = models.BooleanField(default=False)
    # L2 topology using CDP
    enable_box_discovery_cdp = models.BooleanField(default=False)
    # L2 topology using Huawei NDP
    enable_box_discovery_huawei_ndp = models.BooleanField(default=False)
    # L2 topology using MikroTik NDP
    enable_box_discovery_mikrotik_ndp = models.BooleanField(default=False)
    # L2 topology using Foundry FDP
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
    # L2 topology using LACP
    enable_box_discovery_lacp = models.BooleanField(default=False)
    # Enable SLA probes discovery
    enable_box_discovery_sla = models.BooleanField(default=False)
    # Enable CPE discovery
    enable_box_discovery_cpe = models.BooleanField(default=False)
    # Enable MAC discovery
    enable_box_discovery_mac = models.BooleanField(default=False)
    # Enable Housekeeping
    enable_box_discovery_hk = models.BooleanField(default=False)
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
    # Collect mac address table
    enable_periodic_discovery_metrics = models.BooleanField(default=False)
    # Collect ARP cache
    # enable_periodic_discovery_ip = models.BooleanField(default=False)
    #
    clear_links_on_platform_change = models.BooleanField(default=False)
    clear_links_on_serial_change = models.BooleanField(default=False)
    # CPE discovery settings
    cpe_segment_policy = models.CharField(
        _("CPE Segment Policy"),
        max_length=1,
        choices=[
            ("C", "From controller"),
            ("L", "From linked object")
        ],
        default="C"
    )
    cpe_cooldown = models.IntegerField(
        _("CPE cooldown, days"),
        default=0
    )
    cpe_profile = models.ForeignKey(
        "self",
        verbose_name="Object Profile",
        blank=True, null=True
    )
    cpe_auth_profile = models.ForeignKey(
        AuthProfile,
        verbose_name="Auth Profile",
        null=True, blank=True
    )
    #
    hk_handler = models.CharField(
        _("Housekeeping Handler"),
        max_length=255,
        null=True, blank=True
    )
    #
    metrics = PickledField()
    #
    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return ManagedObjectProfile.objects.get(id=id)
        except ManagedObjectProfile.DoesNotExist:
            return None

    def iter_pools(self):
        """
        Iterate all pool instances covered by profile
        """
        for mo in self.managedobject_set.order_by("pool").distinct("pool"):
            yield mo.pool

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

    def on_save(self):
        box_changed = self.initial_data["enable_box_discovery"] != self.enable_box_discovery
        periodic_changed = self.initial_data["enable_periodic_discovery"] != self.enable_periodic_discovery

        if box_changed or periodic_changed:
            call_later(
                "noc.sa.models.managedobjectprofile.apply_discovery_jobs",
                profile_id=self.id,
                box_changed=box_changed,
                periodic_changed=periodic_changed
            )

        if (
            self.initial_data["report_ping_rtt"] != self.report_ping_rtt or
            self.initial_data["enable_ping"] != self.enable_ping or
            self.initial_data["ping_interval"] != self.ping_interval
        ):
            for pool in self.iter_pools():
                ObjectMap.invalidate(pool)


def apply_discovery_jobs(profile_id, box_changed, periodic_changed):
    def iter_objects():
        pool_cache = cachetools.LRUCache(
            maxsize=200,
            missing=lambda x: Pool.objects.get(id=x)
        )
        for o_id, is_managed, pool_id in profile.managedobject_set.values_list("id", "is_managed", "pool"):
            yield o_id, is_managed, pool_cache[pool_id]

    try:
        profile = ManagedObjectProfile.objects.get(id=profile_id)
    except ManagedObjectProfile.DoesNotExist:
        return

    for mo_id, is_managed, pool in iter_objects():
        if box_changed:
            if profile.enable_box_discovery and is_managed:
                Job.submit(
                    "discovery",
                    "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    key=mo_id,
                    pool=pool
                )
            else:
                Job.remove(
                    "discovery",
                    "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    key=mo_id,
                    pool=pool
                )
        if periodic_changed:
            if profile.enable_periodic_discovery and is_managed:
                Job.submit(
                    "discovery",
                    "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    key=mo_id,
                    pool=pool
                )
            else:
                Job.remove(
                    "discovery",
                    "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    key=mo_id,
                    pool=pool
                )
