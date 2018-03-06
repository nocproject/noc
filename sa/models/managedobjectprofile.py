# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
import cachetools
# NOC modules
from noc.main.models.style import Style
from .authprofile import AuthProfile
from noc.lib.validators import is_fqdn
from noc.core.stencil import stencil_registry
from noc.core.model.fields import (TagsField, PickledField,
                                   DocumentReferenceField)
from noc.core.model.decorator import on_save, on_init, on_delete_check
from noc.core.cache.base import cache
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.core.scheduler.job import Job
from noc.core.defer import call_later
from .objectmap import ObjectMap
from noc.sa.interfaces.base import (DictListParameter, ObjectIdParameter, BooleanParameter,
                                    IntParameter, StringParameter)
from noc.core.bi.decorator import bi_sync
from noc.core.window import wf_choices

m_valid = DictListParameter(attrs={
    "metric_type": ObjectIdParameter(required=True),
    "enable_box": BooleanParameter(default=False),
    "enable_periodic": BooleanParameter(default=True),
    "is_stored": BooleanParameter(default=True),
    "window_type": StringParameter(
        choices=["m", "t"],
        default="m"),
    "window": IntParameter(default=1),
    "window_function": StringParameter(choices=[x[0] for x in wf_choices], default="last"),
    "window_config": StringParameter(default=""),
    "window_related": BooleanParameter(default=False),
    "low_error": IntParameter(required=False),
    "high_error": IntParameter(required=False),
    "low_warn": IntParameter(required=False),
    "high_warn": IntParameter(required=False),
    "low_error_weight": IntParameter(default=10),
    "low_warn_weight": IntParameter(default=1),
    "high_warn_weight": IntParameter(default=1),
    "high_error_weight": IntParameter(default=10),
    "threshold_profile": ObjectIdParameter(required=False)
})

id_lock = Lock()


@on_init
@on_save
@bi_sync
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
    # Name restrictions
    # Regular expression to check name format
    name_template = models.CharField(_("Name template"), max_length=256,
                                     blank=True, null=True)
    # IPAM Synchronization
    # During ManagedObject save
    sync_ipam = models.BooleanField(_("Sync. IPAM"), default=False)
    fqdn_template = models.TextField(_("FQDN template"),
                                     null=True, blank=True)
    # @todo: Name validation function
    # FM settings
    enable_ping = models.BooleanField(
        _("Enable ping check"), default=True)
    ping_interval = models.IntegerField(_("Ping interval"), default=60)
    ping_policy = models.CharField(
        _("Ping check policy"),
        max_length=1,
        choices=[
            ("f", "First Success"),
            ("a", "All Successes")
        ],
        default="f"
    )
    ping_size = models.IntegerField(_("Ping packet size"), default=64)
    ping_count = models.IntegerField(_("Ping packets count"), default=3)
    ping_timeout_ms = models.IntegerField(
        _("Ping timeout (ms)"),
        default=1000
    )
    report_ping_rtt = models.BooleanField(
        _("Report RTT"),
        default=False
    )
    report_ping_attempts = models.BooleanField(
        _("Report Attempts"),
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
    # Collect chassis ID information
    enable_box_discovery_id = models.BooleanField(default=False)
    # Collect config
    enable_box_discovery_config = models.BooleanField(default=False)
    # Collect hardware configuration
    enable_box_discovery_asset = models.BooleanField(default=False)
    # Collect hardware configuration
    enable_box_discovery_nri = models.BooleanField(default=False)
    # VRF discovery
    enable_box_discovery_vrf = models.BooleanField(default=False)
    # IP discovery (neighbbors)
    enable_box_discovery_address = models.BooleanField(default=False)
    # IP discovery (interface)
    enable_box_discovery_address_interface = models.BooleanField(default=False)
    # IP discovery (neighbbors)
    enable_box_discovery_prefix = models.BooleanField(default=False)
    # IP discovery (interface)
    enable_box_discovery_prefix_interface = models.BooleanField(default=False)
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
    # Enable metrics
    enable_box_discovery_metrics = models.BooleanField(default=False)
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
    # Collect metrics
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
    # MAC collection settings
    # Collect all MAC addresses
    mac_collect_all = models.BooleanField(default=False)
    # Collect MAC addresses if permitted by interface profile
    mac_collect_interface_profile = models.BooleanField(default=True)
    # Collect MAC addresses from management VLAN
    mac_collect_management = models.BooleanField(default=False)
    # Collect MAC addresses from multicast VLAN
    mac_collect_multicast = models.BooleanField(default=False)
    # Collect MAC from designated VLANs (NetworkSegment/NetworkSegmentProfile)
    mac_collect_vcfilter = models.BooleanField(default=False)
    #
    access_preference = models.CharField(
        "Access Preference",
        max_length=8,
        choices=[
            ("S", "SNMP Only"),
            ("C", "CLI Only"),
            ("SC", "SNMP, CLI"),
            ("CS", "CLI, SNMP")
        ],
        default="CS"
    )
    # Autosegmentation policy
    autosegmentation_policy = models.CharField(
        max_length=1,
        choices=[
            # Do not allow to move object by autosegmentation
            ("d", "Do not segmentate"),
            # Allow moving of object to another segment
            # by autosegmentation process
            ("e", "Allow autosegmentation"),
            # Move seen objects to this object's segment
            ("o", "Segmentate to existing segment"),
            # Expand autosegmentation_segment_name template,
            # ensure that children segment with same name exists
            # then move seen objects to this segment.
            # Following context variables are availale:
            # * object - this object
            # * interface - interface on which remote_object seen from object
            # * remote_object - remote object name
            # To create single segment use templates like {{object.name}}
            # To create segments on per-interface basic use
            # names like {{object.name}}-{{interface.name}}
            ("c", "Segmentate to child segment")
        ],
        default="d"
    )
    # Objects can be autosegmented by *o* and *i* policy
    # only if their level below *autosegmentation_level_limit*
    # 0 - disable
    autosegmentation_level_limit = models.IntegerField(_("Level"), default=0)
    # Jinja2 tempplate for segment name
    # object and interface context variables are exist
    autosegmentation_segment_name = models.CharField(
        max_length=255,
        default="{{object.name}}"
    )
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem,
                                           null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)
    # Object alarms can be escalated
    escalation_policy = models.CharField(
        "Escalation Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable"),
            ("R", "Escalate as Depended")
        ],
        default="E"
    )
    #
    # Raise alarms on discovery problems
    box_discovery_alarm_policy = models.CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable")
        ],
        default="E"
    )
    periodic_discovery_alarm_policy = models.CharField(
        "Periodic Discovery Alarm Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable")
        ],
        default="E"
    )
    box_discovery_fatal_alarm_weight = models.IntegerField(
        "Box Fatal Alarm Weight",
        default=10
    )
    box_discovery_alarm_weight = models.IntegerField(
        "Box Alarm Weight",
        default=1
    )
    periodic_discovery_fatal_alarm_weight = models.IntegerField(
        "Box Fatal Alarm Weight",
        default=10
    )
    periodic_discovery_alarm_weight = models.IntegerField(
        "Periodic Alarm Weight",
        default=1
    )
    # Telemetry
    box_discovery_telemetry_sample = models.IntegerField(
        "Box Discovery Telemetry Sample",
        default=0
    )
    periodic_discovery_telemetry_sample = models.IntegerField(
        "Box Discovery Telemetry Sample",
        default=0
    )
    # CLI Sessions
    cli_session_policy = models.CharField(
        "CLI Session Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable")
        ],
        default="E"
    )
    # CLI privilege policy
    cli_privilege_policy = models.CharField(
        "CLI Privilege Policy",
        max_length=1,
        choices=[
            ("E", "Raise privileges"),
            ("D", "Do not raise")
        ],
        default="E"
    )
    # Event processing policy
    event_processing_policy = models.CharField(
        "Event Processing Policy",
        max_length=1,
        choices=[
            ("E", "Process Events"),
            ("D", "Drop events")
        ],
        default="E"
    )
    # Cache protocol neighbors up to *neighbor_cache_ttl* seconds
    # 0 - disable cache
    neighbor_cache_ttl = models.IntegerField(
        "Neighbor Cache TTL",
        default=0
    )
    #
    metrics = PickledField(blank=True)
    #
    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        mop = ManagedObjectProfile.objects.filter(id=id)[:1]
        if mop:
            return mop[0]
        else:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        mop = ManagedObjectProfile.objects.filter(bi_id=id)[:1]
        if mop:
            return mop[0]
        else:
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
        access_changed = (
            (self.initial_data["access_preference"] != self.access_preference) or
            (self.initial_data["cli_privilege_policy"] != self.cli_privilege_policy)
        )

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
            self.initial_data["ping_interval"] != self.ping_interval or
            self.initial_data["ping_policy"] != self.ping_policy or
            self.initial_data["ping_size"] != self.ping_size or
            self.initial_data["ping_count"] != self.ping_count or
            self.initial_data["ping_timeout_ms"] != self.ping_timeout_ms or
            self.initial_data["report_ping_attempts"] != self.ping_interval or
            self.initial_data["event_processing_policy"] != self.event_processing_policy
        ):
            for pool in self.iter_pools():
                ObjectMap.invalidate(pool)
        if access_changed:
            cache.delete_many([
                "cred-%s" % x
                for x in self.managedobject_set.values_list("id", flat=True)
            ])

    def can_escalate(self, depended=False):
        """
        Check alarms on objects within profile can be escalated
        :return:
        """
        if self.escalation_policy == "R":
            return bool(depended)
        else:
            return self.escalation_policy == "E"

    def can_create_box_alarms(self):
        return self.box_discovery_alarm_policy == "E"

    def can_create_periodic_alarms(self):
        return self.periodic_discovery_alarm_policy == "E"

    def can_cli_session(self):
        return self.cli_session_policy == "E"

    def save(self, force_insert=False, force_update=False, using=None):
        # Validate MeticType for object profile
        if self.metrics:
            try:
                self.metrics = m_valid.clean(self.metrics)
            except ValueError as e:
                raise ValueError(e)
        super(ManagedObjectProfile, self).save(force_insert, force_update)

    @classmethod
    def get_max_metrics_interval(cls, managed_object_profiles=None):
        Q = models.Q
        op_query = ((Q(enable_box_discovery_metrics=True) & Q(enable_box_discovery=True)) |
                    (Q(enable_periodic_discovery=True) & Q(enable_periodic_discovery_metrics=True)))
        if managed_object_profiles:
            op_query &= Q(id__in=managed_object_profiles)
        r = set()
        for mop in ManagedObjectProfile.objects.filter(op_query).exclude(metrics=[]).exclude(metrics=None):
            if not mop.metrics:
                continue
            for m in mop.metrics:
                if m["enable_box"]:
                    r.add(mop.box_discovery_interval)
                if m["enable_periodic"]:
                    r.add(mop.periodic_discovery_interval)
        return max(r) if r else 0


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
