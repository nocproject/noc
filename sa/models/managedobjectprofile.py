# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.config import config
from noc.main.models.style import Style
from noc.core.stencil import stencil_registry
from noc.core.model.fields import TagsField, PickledField, DocumentReferenceField
from noc.core.model.decorator import on_save, on_init, on_delete_check
from noc.core.cache.base import cache
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.handler import Handler
from noc.core.scheduler.job import Job
from noc.core.defer import call_later
from noc.sa.interfaces.base import DictListParameter, ObjectIdParameter, BooleanParameter
from noc.core.bi.decorator import bi_sync
from noc.ip.models.prefixprofile import PrefixProfile
from noc.ip.models.addressprofile import AddressProfile
from noc.vc.models.vpnprofile import VPNProfile
from noc.main.models.extstorage import ExtStorage
from noc.main.models.template import Template
from noc.core.datastream.decorator import datastream
from noc.cm.models.objectvalidationpolicy import ObjectValidationPolicy
from .authprofile import AuthProfile
from .capsprofile import CapsProfile


m_valid = DictListParameter(
    attrs={
        "metric_type": ObjectIdParameter(required=True),
        "enable_box": BooleanParameter(default=False),
        "enable_periodic": BooleanParameter(default=True),
        "is_stored": BooleanParameter(default=True),
        "threshold_profile": ObjectIdParameter(required=False),
    }
)

id_lock = Lock()


@on_init
@on_save
@bi_sync
@datastream
@on_delete_check(
    check=[
        ("sa.ManagedObject", "object_profile"),
        ("sa.ManagedObjectProfile", "cpe_profile"),
        ("sa.ManagedObjectSelector", "filter_object_profile"),
        ("inv.FirmwarePolicy", "object_profile"),
    ]
)
@six.python_2_unicode_compatible
class ManagedObjectProfile(NOCModel):
    class Meta(object):
        verbose_name = _("Managed Object Profile")
        verbose_name_plural = _("Managed Object Profiles")
        db_table = "sa_managedobjectprofile"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    level = models.IntegerField(_("Level"), default=25)
    style = models.ForeignKey(
        Style, verbose_name=_("Style"), blank=True, null=True, on_delete=models.CASCADE
    )
    # Stencils
    shape = models.CharField(
        _("Shape"), blank=True, null=True, choices=stencil_registry.choices, max_length=128
    )
    # Name restrictions
    # Regular expression to check name format
    name_template = models.CharField(_("Name template"), max_length=256, blank=True, null=True)
    # Suffix for ManagedObject's FQDN
    fqdn_suffix = models.CharField(_("FQDN suffix"), max_length=256, null=True, blank=True)
    # Policy for MO address resolution from FQDN
    address_resolution_policy = models.CharField(
        _("Address Resolution Policy"),
        choices=[("D", "Disabled"), ("O", "Once"), ("E", "Enabled")],
        max_length=1,
        null=False,
        blank=False,
        default="D",
    )
    # Name to address resolver. socket.gethostbyname by default
    resolver_handler = DocumentReferenceField(Handler, null=True, blank=True)
    # @todo: Name validation function
    # FM settings
    enable_ping = models.BooleanField(_("Enable ping check"), default=True)
    ping_interval = models.IntegerField(_("Ping interval"), default=60)
    ping_policy = models.CharField(
        _("Ping check policy"),
        max_length=1,
        choices=[("f", "First Success"), ("a", "All Successes")],
        default="f",
    )
    ping_size = models.IntegerField(_("Ping packet size"), default=64)
    ping_count = models.IntegerField(_("Ping packets count"), default=3)
    ping_timeout_ms = models.IntegerField(_("Ping timeout (ms)"), default=1000)
    report_ping_rtt = models.BooleanField(_("Report RTT"), default=False)
    report_ping_attempts = models.BooleanField(_("Report Attempts"), default=False)
    # Additional alarm weight
    weight = models.IntegerField("Alarm weight", default=0)
    #
    card = models.CharField(
        _("Card name"), max_length=256, blank=True, null=True, default="managedobject"
    )
    card_title_template = models.CharField(
        _("Card title template"),
        max_length=256,
        default="{{ object.object_profile.name }}: {{ object.name }}",
    )
    # Enable box discovery.
    # Box discovery launched on system changes
    enable_box_discovery = models.BooleanField(default=True)
    # Interval of periodic discovery when no changes registered
    box_discovery_interval = models.IntegerField(default=86400)
    # Retry interval in case of failure (Object is down)
    box_discovery_failed_interval = models.IntegerField(default=10800)
    # Running policy for box discovery
    box_discovery_running_policy = models.CharField(
        _("Box Running Policy"),
        choices=[("R", _("Require Up")), ("r", _("Require if enabled")), ("i", _("Ignore"))],
        max_length=1,
        default="R",
    )
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
    # Process topology from NRI
    enable_box_discovery_nri = models.BooleanField(default=False)
    # Process NRI portmapping
    enable_box_discovery_nri_portmap = models.BooleanField(default=False)
    # Process NRI service binding
    enable_box_discovery_nri_service = models.BooleanField(default=False)
    # VPN discovery (interface)
    enable_box_discovery_vpn_interface = models.BooleanField(default=False)
    # VPN discovery (MPLS)
    enable_box_discovery_vpn_mpls = models.BooleanField(default=False)
    # VPN discovery (MPLS)
    enable_box_discovery_vpn_confdb = models.BooleanField(default=False)
    # IP discovery (interface)
    enable_box_discovery_address_interface = models.BooleanField(default=False)
    # IP discovery (Management)
    enable_box_discovery_address_management = models.BooleanField(default=False)
    # IP discovery (DHCP)
    enable_box_discovery_address_dhcp = models.BooleanField(default=False)
    # IP discovery (neighbbors)
    enable_box_discovery_address_neighbor = models.BooleanField(default=False)
    # IP discovery (ConfDB)
    enable_box_discovery_address_confdb = models.BooleanField(default=False)
    # IP discovery (interface)
    enable_box_discovery_prefix_interface = models.BooleanField(default=False)
    # IP discovery (neighbbors)
    enable_box_discovery_prefix_neighbor = models.BooleanField(default=False)
    # Prefix discovery (ConfDB)
    enable_box_discovery_prefix_confdb = models.BooleanField(default=False)
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
    # Enable extended MAC discovery
    enable_box_discovery_xmac = models.BooleanField(default=False)
    # Enable metrics
    enable_box_discovery_metrics = models.BooleanField(default=False)
    # Enable Housekeeping
    enable_box_discovery_hk = models.BooleanField(default=False)
    # Enable CPE status
    enable_box_discovery_cpestatus = models.BooleanField(default=False)
    # Enable Box CPE status policy
    box_discovery_cpestatus_policy = models.CharField(
        _("CPE Status Policy"),
        max_length=1,
        choices=[("S", "Status Only"), ("F", "Full")],
        default="S",
    )
    # Enable periodic discovery.
    # Periodic discovery launched repeatedly
    enable_periodic_discovery = models.BooleanField(default=True)
    # Periodic discovery repeat interval
    periodic_discovery_interval = models.IntegerField(default=300)
    periodic_discovery_running_policy = models.CharField(
        _("Periodic Running Policy"),
        choices=[("R", _("Require Up")), ("r", _("Require if enabled")), ("i", _("Ignore"))],
        max_length=1,
        default="R",
    )
    # Collect uptime
    enable_periodic_discovery_uptime = models.BooleanField(default=False)
    # Collect interface status
    enable_periodic_discovery_interface_status = models.BooleanField(default=False)
    # Collect mac address table
    enable_periodic_discovery_mac = models.BooleanField(default=False)
    # Collect metrics
    enable_periodic_discovery_metrics = models.BooleanField(default=False)
    # Enable CPE status
    enable_periodic_discovery_cpestatus = models.BooleanField(default=False)
    # CPE status discovery settings
    periodic_discovery_cpestatus_policy = models.CharField(
        _("CPE Status Policy"),
        max_length=1,
        choices=[("S", "Status Only"), ("F", "Full")],
        default="S",
    )
    # Collect ARP cache
    # enable_periodic_discovery_ip = models.BooleanField(default=False)
    #
    clear_links_on_platform_change = models.BooleanField(default=False)
    clear_links_on_serial_change = models.BooleanField(default=False)
    # CPE discovery settings
    cpe_segment_policy = models.CharField(
        _("CPE Segment Policy"),
        max_length=1,
        choices=[("C", "From controller"), ("L", "From linked object")],
        default="C",
    )
    cpe_cooldown = models.IntegerField(_("CPE cooldown, days"), default=0)
    cpe_profile = models.ForeignKey(
        "self", verbose_name="Object Profile", blank=True, null=True, on_delete=models.CASCADE
    )
    cpe_auth_profile = models.ForeignKey(
        AuthProfile, verbose_name="Auth Profile", null=True, blank=True, on_delete=models.CASCADE
    )
    #
    hk_handler = DocumentReferenceField(Handler, null=True, blank=True)
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
        choices=[("S", "SNMP Only"), ("C", "CLI Only"), ("SC", "SNMP, CLI"), ("CS", "CLI, SNMP")],
        default="CS",
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
            ("c", "Segmentate to child segment"),
        ],
        default="d",
    )
    # Objects can be autosegmented by *o* and *i* policy
    # only if their level below *autosegmentation_level_limit*
    # 0 - disable
    autosegmentation_level_limit = models.IntegerField(_("Level"), default=0)
    # Jinja2 tempplate for segment name
    # object and interface context variables are exist
    autosegmentation_segment_name = models.CharField(max_length=255, default="{{object.name}}")
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)
    # Caps discovery settings
    caps_profile = DocumentReferenceField(
        CapsProfile, null=False, blank=False, default=CapsProfile.get_default_profile
    )
    # Object alarms can be escalated
    escalation_policy = models.CharField(
        "Escalation Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("R", "Escalate as Depended")],
        default="E",
    )
    # Raise alarms on discovery problems
    box_discovery_alarm_policy = models.CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable")],
        default="E",
    )
    periodic_discovery_alarm_policy = models.CharField(
        "Periodic Discovery Alarm Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable")],
        default="E",
    )
    box_discovery_fatal_alarm_weight = models.IntegerField("Box Fatal Alarm Weight", default=10)
    box_discovery_alarm_weight = models.IntegerField("Box Alarm Weight", default=1)
    periodic_discovery_fatal_alarm_weight = models.IntegerField(
        "Box Fatal Alarm Weight", default=10
    )
    periodic_discovery_alarm_weight = models.IntegerField("Periodic Alarm Weight", default=1)
    # Telemetry
    box_discovery_telemetry_sample = models.IntegerField(
        "Box Discovery Telemetry Sample", default=0
    )
    periodic_discovery_telemetry_sample = models.IntegerField(
        "Box Discovery Telemetry Sample", default=0
    )
    # CLI Sessions
    cli_session_policy = models.CharField(
        "CLI Session Policy", max_length=1, choices=[("E", "Enable"), ("D", "Disable")], default="E"
    )
    # CLI privilege policy
    cli_privilege_policy = models.CharField(
        "CLI Privilege Policy",
        max_length=1,
        choices=[("E", "Raise privileges"), ("D", "Do not raise")],
        default="E",
    )
    # Event processing policy
    event_processing_policy = models.CharField(
        "Event Processing Policy",
        max_length=1,
        choices=[("E", "Process Events"), ("D", "Drop events")],
        default="E",
    )
    # Collect and archive syslog events
    syslog_archive_policy = models.CharField(
        "SYSLOG Archive Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable")],
        default="D",
    )
    # Cache protocol neighbors up to *neighbor_cache_ttl* seconds
    # 0 - disable cache
    neighbor_cache_ttl = models.IntegerField("Neighbor Cache TTL", default=0)
    # VPN discovery profiles
    vpn_profile_interface = DocumentReferenceField(VPNProfile, null=True, blank=True)
    vpn_profile_mpls = DocumentReferenceField(VPNProfile, null=True, blank=True)
    vpn_profile_confdb = DocumentReferenceField(VPNProfile, null=True, blank=True)
    # Prefix discovery profiles
    prefix_profile_interface = DocumentReferenceField(PrefixProfile, null=True, blank=True)
    prefix_profile_neighbor = DocumentReferenceField(PrefixProfile, null=True, blank=True)
    prefix_profile_confdb = DocumentReferenceField(PrefixProfile, null=True, blank=True)
    # Address discovery profiles
    address_profile_interface = DocumentReferenceField(AddressProfile, null=True, blank=True)
    address_profile_management = DocumentReferenceField(AddressProfile, null=True, blank=True)
    address_profile_dhcp = DocumentReferenceField(AddressProfile, null=True, blank=True)
    address_profile_neighbor = DocumentReferenceField(AddressProfile, null=True, blank=True)
    address_profile_confdb = DocumentReferenceField(AddressProfile, null=True, blank=True)
    # Config policy
    config_policy = models.CharField(
        _("Config Policy"),
        max_length=1,
        choices=[
            ("s", "Script"),
            ("S", "Script, Download"),
            ("D", "Download, Script"),
            ("d", "Download"),
        ],
        default="s",
    )
    config_download_storage = DocumentReferenceField(ExtStorage, null=True, blank=True)
    config_download_template = models.ForeignKey(
        Template,
        verbose_name=_("Config Mirror Template"),
        blank=True,
        null=True,
        related_name="config_download_objects_set",
        on_delete=models.CASCADE,
    )
    config_fetch_policy = models.CharField(
        _("Config Fetch Policy"),
        max_length=1,
        choices=[("s", "Startup"), ("r", "Running")],
        default="r",
    )
    # Config mirror settings
    config_mirror_storage = DocumentReferenceField(ExtStorage, null=True, blank=True)
    config_mirror_template = models.ForeignKey(
        Template,
        verbose_name=_("Config Mirror Template"),
        blank=True,
        null=True,
        related_name="config_mirror_objects_set",
        on_delete=models.CASCADE,
    )
    config_mirror_policy = models.CharField(
        _("Config Mirror Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("A", "Always"), ("C", "Change")],
        default="C",
    )
    # Config validation settings
    config_validation_policy = models.CharField(
        _("Config Validation Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("A", "Always"), ("C", "Change")],
        default="C",
    )
    object_validation_policy = DocumentReferenceField(ObjectValidationPolicy, null=True, blank=True)
    # Interface discovery settings
    interface_discovery_policy = models.CharField(
        _("Interface Discovery Policy"),
        max_length=1,
        choices=[
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="s",
    )
    # Caps discovery settings
    caps_discovery_policy = models.CharField(
        _("Caps Discovery Policy"),
        max_length=1,
        choices=[
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="s",
    )
    # VLAN discovery settings
    vlan_discovery_policy = models.CharField(
        _("VLAN Discovery Policy"),
        max_length=1,
        choices=[
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="s",
    )
    # Behaviour on new platform detection in version check
    new_platform_creation_policy = models.CharField(
        _("New Platform Creation Policy"),
        max_length=1,
        choices=[("C", "Create"), ("A", "Alarm")],
        default="C",
    )
    # Behavior on denied firmware detection
    denied_firmware_policy = models.CharField(
        _("Firmware Policy"),
        max_length=1,
        choices=[
            ("I", "Ignore"),
            ("s", "Ignore&Stop"),
            ("A", "Raise Alarm"),
            ("S", "Raise Alarm&Stop"),
        ],
        default="I",
    )
    # Beef collection settings
    beef_storage = DocumentReferenceField(ExtStorage, null=True, blank=True)
    beef_path_template = models.ForeignKey(
        Template,
        verbose_name=_("Beef Path Template"),
        blank=True,
        null=True,
        related_name="beef_objects_set",
        on_delete=models.CASCADE,
    )
    beef_policy = models.CharField(
        _("Beef Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("A", "Always"), ("C", "Change")],
        default="D",
    )
    # ConfDB policies
    confdb_raw_policy = models.CharField(
        _("ConfDB Raw Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("E", "Enable")],
        default="D",
    )
    #
    metrics = PickledField(blank=True)
    #
    tags = TagsField("Tags", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
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

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        if config.datastream.enable_managedobject and changed_fields.intersection(
            {"name", "remote_system", "remote_id"}
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "managedobject", mo_id
        if config.datastream.enable_cfgping and changed_fields.intersection(
            {
                "enable_ping",
                "ping_interval",
                "ping_policy",
                "ping_size",
                "ping_count",
                "ping_timeout_ms",
                "report_ping_rtt",
                "report_ping_attempts",
                "event_processing_policy",
            }
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "cfgping", mo_id
        if config.datastream.enable_cfgsyslog and changed_fields.intersection(
            {"event_processing_policy", "syslog_archive_policy"}
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "cfgsyslog", mo_id
        if config.datastream.enable_cfgtrap and "event_processing_policy" in changed_fields:
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "cfgtrap", mo_id

    def iter_pools(self):
        """
        Iterate all pool instances covered by profile
        """
        for mo in self.managedobject_set.order_by("pool").distinct("pool"):
            yield mo.pool

    def on_save(self):
        box_changed = self.initial_data["enable_box_discovery"] != self.enable_box_discovery
        periodic_changed = (
            self.initial_data["enable_periodic_discovery"] != self.enable_periodic_discovery
        )
        access_changed = (self.initial_data["access_preference"] != self.access_preference) or (
            self.initial_data["cli_privilege_policy"] != self.cli_privilege_policy
        )

        if box_changed or periodic_changed:
            call_later(
                "noc.sa.models.managedobjectprofile.apply_discovery_jobs",
                profile_id=self.id,
                box_changed=box_changed,
                periodic_changed=periodic_changed,
            )
        if access_changed:
            cache.delete_many(
                ["cred-%s" % x for x in self.managedobject_set.values_list("id", flat=True)]
            )

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

    def save(self, *args, **kwargs):
        # Validate MeticType for object profile
        if self.metrics:
            try:
                self.metrics = m_valid.clean(self.metrics)
            except ValueError as e:
                raise ValueError(e)
        super(ManagedObjectProfile, self).save(*args, **kwargs)

    @classmethod
    def get_max_metrics_interval(cls, managed_object_profiles=None):
        Q = models.Q
        op_query = (Q(enable_box_discovery_metrics=True) & Q(enable_box_discovery=True)) | (
            Q(enable_periodic_discovery=True) & Q(enable_periodic_discovery_metrics=True)
        )
        if managed_object_profiles:
            op_query &= Q(id__in=managed_object_profiles)
        r = set()
        for mop in (
            ManagedObjectProfile.objects.filter(op_query).exclude(metrics=[]).exclude(metrics=None)
        ):
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
        pool_cache = cachetools.LRUCache(maxsize=200)
        pool_cache.__missing__ = lambda x: Pool.objects.get(id=x)
        for o_id, is_managed, pool_id in profile.managedobject_set.values_list(
            "id", "is_managed", "pool"
        ):
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
                    pool=pool,
                )
            else:
                Job.remove(
                    "discovery",
                    "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    key=mo_id,
                    pool=pool,
                )
        if periodic_changed:
            if profile.enable_periodic_discovery and is_managed:
                Job.submit(
                    "discovery",
                    "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    key=mo_id,
                    pool=pool,
                )
            else:
                Job.remove(
                    "discovery",
                    "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    key=mo_id,
                    pool=pool,
                )
