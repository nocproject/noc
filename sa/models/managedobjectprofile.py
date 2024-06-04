# ----------------------------------------------------------------------
# ManagedObjectProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import datetime
from threading import Lock
from functools import partial
from dataclasses import dataclass
from typing import Optional, List, Dict, Iterable, Any, Set

# Third-party modules
import cachetools
import orjson
from django.db import connection as pg_connection
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.query_utils import Q as d_Q
from pydantic import BaseModel, RootModel, field_validator

# NOC modules
from noc.core.translation import ugettext as _
from noc.core.model.base import NOCModel
from noc.core.stencil import stencil_registry
from noc.core.model.fields import DocumentReferenceField, PydanticField
from noc.core.model.decorator import on_save, on_init, on_delete_check
from noc.core.cache.base import cache
from noc.main.models.style import Style
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.handler import Handler
from noc.main.models.label import Label
from noc.core.scheduler.job import Job
from noc.core.bi.decorator import bi_sync
from noc.core.defer import call_later, defer
from noc.core.topology.types import ShapeOverlayPosition, ShapeOverlayForm
from noc.core.script.scheme import SSH
from noc.core.wf.interaction import Interaction
from noc.core.wf.diagnostic import (
    PROFILE_DIAG,
    SNMP_DIAG,
    CLI_DIAG,
    HTTP_DIAG,
    SNMPTRAP_DIAG,
    SYSLOG_DIAG,
    DIAGNOCSTIC_LABEL_SCOPE,
    DiagnosticState,
    DiagnosticConfig,
    DiagnosticHub,
    Check,
)
from noc.sa.interfaces.base import (
    DictListParameter,
    ObjectIdParameter,
    BooleanParameter,
    IntParameter,
)
from noc.ip.models.prefixprofile import PrefixProfile
from noc.ip.models.addressprofile import AddressProfile
from noc.main.models.extstorage import ExtStorage
from noc.main.models.template import Template
from noc.core.change.decorator import change
from noc.cm.models.objectvalidationpolicy import ObjectValidationPolicy
from noc.inv.models.ifdescpatterns import IfDescPatterns
from noc.main.models.glyph import Glyph
from noc.pm.models.metrictype import MetricType
from noc.vc.models.vlanfilter import VLANFilter
from noc.vc.models.vpnprofile import VPNProfile
from noc.wf.models.workflow import Workflow
from .capsprofile import CapsProfile
from noc.config import config

metrics_lock = Lock()


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    is_stored: bool
    interval: int


class ModelMetricConfigItem(BaseModel):
    metric_type: str
    is_stored: bool = True
    interval: Optional[int] = 0

    def __str__(self):
        return self.metric_type


MetricConfigItems = RootModel[List[ModelMetricConfigItem]]


class MatchRule(BaseModel):
    dynamic_order: int = 0
    labels: List[str] = []
    handler: Optional[str]

    @field_validator("handler")
    def handler_must_handler(cls, v):  # pylint: disable=no-self-argument
        if not v:
            return v
        h = Handler.objects.filter(id=v).first()
        if not h:
            raise ValueError(f"[{h}] Handler not found")
        elif not h.allow_match_rule:
            raise ValueError(f"[{h}] Handler must be set Allow Match Rule")
        return str(h.id)


MatchRules = RootModel[List[Optional[MatchRule]]]


m_valid = DictListParameter(
    attrs={
        "metric_type": ObjectIdParameter(required=True),
        "is_stored": BooleanParameter(default=True),
        "interval": IntParameter(min_value=0, required=False),
    }
)

id_lock = Lock()


@Label.match_labels("managedobjectprofile", allowed_op={"="})
@Label.model
@on_init
@on_save
@bi_sync
@change
@on_delete_check(
    check=[
        ("sa.ManagedObject", "object_profile"),
        ("inv.CPEProfile", "object_profile"),
    ],
    clean_lazy_labels="managedobjectprofile",
)
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
    # Workflow
    workflow: "Workflow" = DocumentReferenceField(
        Workflow,
        null=False,
        blank=False,
        default=partial(Workflow.get_default_workflow, "sa.ManagedObjectProfile"),
    )
    # Stencils
    shape = models.CharField(
        _("Shape"), blank=True, null=True, choices=stencil_registry.choices, max_length=128
    )
    shape_overlay_glyph = DocumentReferenceField(Glyph, null=True, blank=True)
    shape_overlay_position = models.CharField(
        "S.O. Position",
        max_length=2,
        choices=[(x.value, x.value) for x in ShapeOverlayPosition],
        null=True,
        blank=True,
    )
    shape_overlay_form = models.CharField(
        "S.O. Form",
        max_length=1,
        choices=[(x.value, x.value) for x in ShapeOverlayForm],
        null=True,
        blank=True,
    )
    shape_title_template = models.CharField(
        _("Shape Title template"), max_length=256, blank=True, null=True
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
    ping_time_expr_policy = models.CharField(
        _("Policy Off Hours"),
        choices=[("D", _("Disable ping")), ("E", _("Enable ping but dont follow status"))],
        max_length=1,
        default="D",
    )
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
    # Enable extended MAC discovery
    enable_box_discovery_xmac = models.BooleanField(default=False)
    # Enable interface description discovery
    enable_box_discovery_ifdesc = models.BooleanField(default=False)
    # Enable Housekeeping
    enable_box_discovery_hk = models.BooleanField(default=False)
    # Enable Config Param Data Discovery
    enable_box_discovery_param_data = models.BooleanField(default=False)
    # Resovle conflict when discovery diff value from object
    box_discovery_param_data_conflict_resolve_policy = models.CharField(
        _("Box ParamData Conflict Resolve Policy"),
        max_length=1,
        choices=[("M", "Manual"), ("D", "Prefer Discovery"), ("O", "Prefer Object")],
        default="O",
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
    periodic_discovery_uptime_interval = models.IntegerField(default=0)
    # Collect interface status
    enable_periodic_discovery_interface_status = models.BooleanField(default=False)
    periodic_discovery_interface_status_interval = models.IntegerField(default=300)
    # Collect mac address table
    enable_periodic_discovery_mac = models.BooleanField(default=False)
    periodic_discovery_mac_interval = models.IntegerField(default=0)
    # A - Collect all MAC addresses, I - Collect MAC allowed by Interface Profile
    periodic_discovery_mac_filter_policy = models.CharField(
        _("Periodic MAC Collect Policy"),
        max_length=1,
        choices=[("I", "Interface Profile"), ("A", "All")],
        default="A",
    )
    mac_collect_vlanfilter = DocumentReferenceField(VLANFilter, null=True, blank=True)
    # Collect metrics
    enable_metrics = models.BooleanField(default=False)
    # Enable Alarms
    enable_periodic_discovery_alarms = models.BooleanField(default=False)
    periodic_discovery_alarms_interval = models.IntegerField(default=0)
    # Enable CPE status
    enable_periodic_discovery_cpestatus = models.BooleanField(default=False)
    periodic_discovery_cpestatus_interval = models.IntegerField(default=0)
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
    #
    hk_handler = DocumentReferenceField(Handler, null=True, blank=True)
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
    # Auto-create interface to link
    enable_interface_autocreation = models.BooleanField(default=False)
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
    # VLAN Discovery
    vlan_interface_discovery = models.CharField(
        "VLAN Interface Discovery Policy",
        max_length=1,
        choices=[
            ("D", "Disable"),
            ("S", "Status Only"),
            ("C", "Create only"),
            ("V", "Create & Status"),
        ],
        default="D",
    )
    vlan_vlandb_discovery = models.CharField(
        "VLAN DB Discovery Policy",
        max_length=1,
        choices=[
            ("D", "Disable"),
            ("S", "Status Only"),
            ("C", "Create only"),
            ("V", "Create & Status"),
        ],
        default="D",
    )
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
    # ifdesc settings
    ifdesc_patterns = DocumentReferenceField(IfDescPatterns, null=True, blank=True)
    ifdesc_handler = DocumentReferenceField(Handler, null=True, blank=True)
    ifdesc_symmetric = models.BooleanField(default=False)
    # xRCA settings
    enable_rca_downlink_merge = models.BooleanField(default=False)
    rca_downlink_merge_window = models.IntegerField(default=120)
    # Abduct Detection settings
    abduct_detection_window = models.IntegerField(default=0)
    abduct_detection_threshold = models.IntegerField(default=0)
    # Limits
    snmp_rate_limit = models.IntegerField(default=0)
    #
    metrics_default_interval = models.IntegerField(default=300, validators=[MinValueValidator(0)])
    #
    metrics: List[ModelMetricConfigItem] = PydanticField(
        "Metric Config Items",
        schema=MetricConfigItems,
        blank=True,
        null=True,
        default=list,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )
    #
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    # Dynamic Profile Classification
    dynamic_classification_policy = models.CharField(
        _("Dynamic Classification Policy"),
        max_length=1,
        choices=[("D", "Disable"), ("R", "By Rule")],
        default="R",
    )
    match_rules = PydanticField(
        _("Match Dynamic Rules"),
        schema=MatchRules,
        blank=True,
        null=True,
        default=list,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )
    # Trapcollector Storm Policy
    trapcollector_storm_policy = models.CharField(
        _("Trapcollector Storm Policy"),
        max_length=1,
        choices=[
            ("D", "Disabled"),
            ("B", "Block"),
            ("R", "Raise Alarm"),
            ("A", "Block & Raise Alarm"),
        ],
        default="D",
    )
    # Trapcollector Storm Threshold
    trapcollector_storm_threshold = models.IntegerField(default=1000)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _object_profile_metrics = cachetools.TTLCache(maxsize=1000, ttl=300)

    DEFAULT_WORKFLOW_NAME = "ManagedObject Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["ManagedObjectProfile"]:
        return ManagedObjectProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["ManagedObjectProfile"]:
        return ManagedObjectProfile.objects.filter(bi_id=bi_id).first()

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        changed_fields = set(changed_fields or [])
        if config.datastream.enable_managedobject and changed_fields.intersection(
            {
                "name",
                "remote_system",
                "remote_id",
                "enable_box_discovery",
                "enable_periodic_discovery",
                "enable_ping",
                "labels",
                "level",
            }
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "managedobject", mo_id
        if config.datastream.enable_cfgtarget and changed_fields.intersection(
            {
                "enable_ping",
                "ping_interval",
                "ping_policy",
                "ping_size",
                "ping_count",
                "ping_timeout_ms",
                "ping_time_expr_policy",
                "report_ping_rtt",
                "report_ping_attempts",
                "event_processing_policy",
                "syslog_archive_policy",
            }
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "id", flat=True
            ):
                yield "cfgtarget", mo_id
        if config.datastream.enable_cfgmetricsources and (
            "metrics" in changed_fields
            or "enable_metrics" in changed_fields
            or "metrics_default_interval" in changed_fields
        ):
            for mo_id in ManagedObject.objects.filter(object_profile=self).values_list(
                "bi_id", flat=True
            ):
                yield "cfgmetricsources", f"sa.ManagedObject::{mo_id}"

    def iter_pools(self):
        """
        Iterate all pool instances covered by profile
        """
        for mo in self.managedobject_set.order_by("pool").distinct("pool"):
            yield mo.pool

    def can_escalate(self, depended=False):
        """
        Check alarms on objects within profile can be escalated
        :return:
        """
        if self.escalation_policy == "R":
            return bool(depended)
        return self.escalation_policy == "E"

    def can_create_box_alarms(self):
        return self.box_discovery_alarm_policy == "E"

    def can_create_periodic_alarms(self):
        return self.periodic_discovery_alarm_policy == "E"

    def can_cli_session(self):
        return self.cli_session_policy == "E"

    def is_field_changed(self, fields: List[str]) -> bool:
        for f in fields:
            if f in self.initial_data and self.initial_data[f] != getattr(self, f):
                return True
        return False

    def get_changed_diagnostics(self) -> Set[str]:
        """
        Return changed diagnostic state by policy field
        """
        r = set()
        if self.is_field_changed(["event_processing_policy"]):
            r |= {SNMPTRAP_DIAG, SYSLOG_DIAG}
        if (
            self.is_field_changed(["enable_box_discovery_profile"])
            and not self.enable_box_discovery_profile
        ):
            r |= {PROFILE_DIAG}
        if self.is_field_changed(["enable_box_discovery"]) and not self.enable_box_discovery:
            r |= {CLI_DIAG, SNMP_DIAG, PROFILE_DIAG}
        if not self.is_field_changed(["access_preference"]):
            return r
        if not self.initial_data.get("access_preference", []):
            r |= {CLI_DIAG, SNMP_DIAG}
        elif set(self.access_preference) != set(self.initial_data["access_preference"]):
            # Same preference
            same_preference = set(self.initial_data["access_preference"]).intersection(
                set(self.access_preference)
            )
            # Change preference - all sub same
            for p in {"S", "C"} - same_preference:
                r.add({"S": SNMP_DIAG, "C": CLI_DIAG}[p])
        return r

    def on_save(self):
        """
        Run jobs after change fields
        * access policy - reset credential cache and save diagnostics
        * job enable - ensure objects jobs
        * event policy - change diagnostic
        """
        from .managedobject import CREDENTIAL_CACHE_VERSION, MANAGEDOBJECT_CACHE_VERSION

        box_changed = self.is_field_changed(["enable_box_discovery"])
        periodic_changed = self.is_field_changed(["enable_periodic_discovery", "enable_metrics"])
        alarm_box_changed = self.is_field_changed(["box_discovery_alarm_policy"])
        access_changed = self.is_field_changed(
            [
                "access_preference",
                "cli_privilege_policy",
                "beef_storage",
                "beef_path_template",
                "snmp_rate_limit",
            ]
        )
        if box_changed or periodic_changed:
            defer(
                "noc.sa.models.managedobjectprofile.apply_discovery_jobs",
                key=self.id,
                profile_id=self.id,
                box_changed=box_changed,
                periodic_changed=periodic_changed,
            )
        if box_changed or periodic_changed or alarm_box_changed:
            defer(
                "noc.sa.models.managedobjectprofile.update_diagnostics_alarms",
                key=self.id,
                profile_id=self.id,
            )
        if access_changed:
            cache.delete_many(
                [f"cred-{x}" for x in self.managedobject_set.values_list("id", flat=True)],
                version=CREDENTIAL_CACHE_VERSION,
            )
        if self.is_field_changed(["enable_rca_downlink_merge", "rca_downlink_merge_window"]):
            if config.topo.enable_scheduler_task:
                call_later("noc.core.topology.uplink.update_uplinks", 30)
        if self.is_field_changed(["level", "weight", "labels", "escalation_policy"]):
            cache.delete_many(
                [
                    f"managedobject-id-{x}"
                    for x in self.managedobject_set.values_list("id", flat=True)
                ],
                version=MANAGEDOBJECT_CACHE_VERSION,
            )
        cd = self.get_changed_diagnostics()
        # box_changed
        # self.diagnostic.reset_diagnostics([PROFILE_DIAG, SNMP_DIAG, CLI_DIAG])
        # print("Diagnostic Changed", self.get_changed_diagnostics())
        if not cd and self.is_field_changed(["level", "weight", "labels", "escalation_policy"]):
            cache.delete_many(
                [
                    f"managedobject-id-{x}"
                    for x in self.managedobject_set.values_list("id", flat=True)
                ],
                version=MANAGEDOBJECT_CACHE_VERSION,
            )
            return
        now = datetime.datetime.now().replace(microsecond=0)
        alarm_sync = False
        for dc in self.iter_diagnostic_configs():
            if dc.diagnostic not in cd:
                continue
            d_state = DiagnosticState.blocked if dc.blocked else DiagnosticState.unknown
            diags = {
                dc.diagnostic: {
                    "diagnostic": dc.diagnostic,
                    "state": d_state,
                    "reason": "Blocked by Profile settings",
                    "checks": [],
                    "changed": now,
                }
            }
            policy_field = "access_preference"
            if dc.diagnostic in {SNMPTRAP_DIAG, SYSLOG_DIAG}:
                policy_field = "event_processing_policy"
            if dc.diagnostic in {CLI_DIAG, SNMP_DIAG, PROFILE_DIAG} and dc.blocked:
                alarm_sync = True
            # Update diagnostics
            with pg_connection.cursor() as cursor:
                cursor.execute(
                    f"""
                     UPDATE sa_managedobject
                     SET diagnostics = diagnostics || %s::jsonb
                     WHERE {policy_field} = %s and object_profile_id = %s""",
                    [orjson.dumps(diags).decode("utf-8"), "P", self.id],
                )
            # change labels :f"{DIAGNOCSTIC_LABEL_SCOPE}::{d.diagnostic}::{d.state}"
            r_labels = []
            if d_state != DiagnosticState.blocked:
                r_labels = [
                    f"{DIAGNOCSTIC_LABEL_SCOPE}::{dc.diagnostic}::{DiagnosticState.blocked.value}"
                ]
            else:
                # All state
                r_labels = [
                    f"{DIAGNOCSTIC_LABEL_SCOPE}::{dc.diagnostic}::{s.value}"
                    for s in DiagnosticState
                    if not s.is_blocked
                ]
            Label._change_model_labels(
                "sa.ManagedObject",
                add_labels=[f"{DIAGNOCSTIC_LABEL_SCOPE}::{dc.diagnostic}::{d_state}"],
                remove_labels=r_labels,
                instance_filters=[("object_profile_id", self.id), (policy_field, "P")],
            )
        cache.delete_many(
            [f"managedobject-id-{x}" for x in self.managedobject_set.values_list("id", flat=True)],
            version=MANAGEDOBJECT_CACHE_VERSION,
        )
        if self.box_discovery_alarm_policy != "D" and (alarm_sync or not self.enable_box_discovery):
            # Sync alarm
            defer(
                "noc.sa.models.managedobjectprofile.update_diagnostics_alarms",
                key=self.id,
                profile_id=self.id,
            )

    def iter_diagnostic_configs(self, o=None) -> Iterable[DiagnosticConfig]:
        """
        Iterate over object diagnostics
        :param o: ManagedObject
        :return:
        """
        if o:
            ac = o.get_access_preference()
            snmp_cred = o.credentials.get_snmp_credential()
        else:
            ac = self.access_preference
            snmp_cred = None
        if not o or Interaction.ServiceActivation in o.interactions:
            # SNMP Diagnostic
            yield DiagnosticConfig(
                SNMP_DIAG,
                display_description="Check Device response by SNMP request",
                checks=[
                    Check(
                        name="SNMPv1",
                        credential=snmp_cred,
                    ),
                    Check(
                        name="SNMPv2c",
                        credential=snmp_cred,
                    ),
                    Check(
                        name="SNMPv3",
                        credential=snmp_cred,
                    ),
                ],
                blocked=ac == "C",
                run_policy="F",
                run_order="S",
                discovery_box=True,
                alarm_class="NOC | Managed Object | Access Lost",
                alarm_labels=["noc::access::method::SNMP"],
                reason="Blocked by AccessPreference" if ac == "C" else None,
            )
            yield DiagnosticConfig(
                PROFILE_DIAG,
                display_description="Check device profile",
                show_in_display=False,
                checks=[
                    Check(name="PROFILE", credential=snmp_cred),
                ],
                alarm_class="Discovery | Guess | Profile",
                blocked=not self.enable_box_discovery_profile,
                run_policy="A",
                run_order="S",
                discovery_box=True,
                reason="Profile Discovery " if not self.enable_box_discovery_profile else None,
            )
            blocked = ac == "S"
            # CLI Diagnostic
            if o:
                blocked |= o.scheme not in {1, 2}
                cli_cred = o.credentials.get_cli_credential()
            else:
                cli_cred = None
            checks = [
                Check(
                    name="TELNET",
                    credential=cli_cred,
                ),
                Check(
                    name="SSH",
                    credential=cli_cred,
                ),
            ]
            if o and o.scheme == SSH:
                checks.reverse()
            yield DiagnosticConfig(
                CLI_DIAG,
                display_description="Check Device response by CLI (TELNET/SSH) request",
                checks=checks,
                discovery_box=True,
                alarm_class="NOC | Managed Object | Access Lost",
                alarm_labels=["noc::access::method::CLI"],
                blocked=blocked,
                run_policy="F",
                run_order="S",
                reason="Blocked by AccessPreference" if blocked else None,
            )
            # HTTP Diagnostic
            yield DiagnosticConfig(
                HTTP_DIAG,
                display_description="Check Device response by HTTP/HTTPS request",
                show_in_display=False,
                alarm_class="NOC | Managed Object | Access Lost",
                alarm_labels=["noc::access::method::HTTP"],
                checks=[Check("HTTP"), Check("HTTPS")],
                blocked=False,
                run_policy="D",  # Not supported
                run_order="S",
                reason=None,
            )
        # Access Diagnostic (Blocked - block SNMP & CLI Check ?
        yield DiagnosticConfig(
            "Access",
            dependent=["SNMP", "CLI", "HTTP"],
            show_in_display=False,
            alarm_class="NOC | Managed Object | Access Degraded",
        )
        if not o or Interaction.Event in o.interactions:
            fm_policy = o.get_event_processing_policy() if o else self.event_processing_policy
            blocked, reason = False, ""
            if fm_policy == "d":
                blocked, reason = True, "Disable by Event Processing policy"
            elif o and o.trap_source_type == "d":
                blocked, reason = True, "Disable by source settings"
            # FM
            yield DiagnosticConfig(
                # Reset if change IP/Policy change
                SNMPTRAP_DIAG,
                display_description="Received SNMP Trap from device",
                blocked=blocked,
                run_policy="D",
                reason=reason,
            )
            blocked, reason = False, ""
            if fm_policy == "d":
                blocked, reason = True, "Disable by Event Processing policy"
            elif o and o.syslog_source_type == "d":
                blocked, reason = True, "Disable by source settings"
            yield DiagnosticConfig(
                # Reset if change IP/Policy change
                SYSLOG_DIAG,
                display_description="Received SYSLOG from device",
                blocked=blocked,
                run_policy="D",
                reason=reason,
            )

    @classmethod
    def get_max_metrics_interval(cls, managed_object_profiles=None):
        Q = models.Q
        op_query = Q(enable_metrics=True)
        if managed_object_profiles:
            op_query &= Q(id__in=managed_object_profiles)
        r = set()
        for mop in (
            ManagedObjectProfile.objects.filter(op_query).exclude(metrics=[]).exclude(metrics=None)
        ):
            if not mop.metrics:
                continue
            r.add(mop.metrics_default_interval)
            for m in mop.metrics:
                if m.get("interval", 0):
                    r.add(m["interval"])
        return max(r) if r else 0

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_managedobjectprofile")

    @classmethod
    def iter_lazy_labels(cls, object_profile: "ManagedObjectProfile"):
        yield f"noc::managedobjectprofile::{object_profile.name}::="

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_object_profile_metrics"), lock=lambda _: metrics_lock
    )
    def get_object_profile_metrics(cls, p_id: int) -> Dict[str, MetricConfig]:
        r = {}
        opr = ManagedObjectProfile.get_by_id(id=p_id)
        if not opr:
            return r
        for m in opr.metrics:
            mt_id = m.get("metric_type")
            if not mt_id:
                continue
            mt = MetricType.get_by_id(mt_id)
            if not mt:
                continue
            r[mt.name] = MetricConfig(
                mt, m.get("is_stored", True), m.get("interval") or opr.metrics_default_interval
            )
        return r

    def get_metric_discovery_interval(self) -> int:
        r = [m.get("interval") or self.metrics_default_interval for m in self.metrics]
        return min(r) if r else self.metrics_default_interval


@dataclass
class GenericObject(object):
    id: int
    object_profile: int
    diagnostics: Dict[str, Any]
    effective_labels: List[str]
    pool: str = "default"
    access_preference = "S"

    @property
    def alarms_stream_and_partition(self):
        return f"dispose.{self.pool}", 0

    def iter_diagnostic_configs(self):
        mop = ManagedObjectProfile.objects.get(id=int(self.object_profile))
        yield from mop.iter_diagnostic_configs()


def update_diagnostics_alarms(profile_id, **kwargs):
    """
    Update diagnostic statuses
    * if disable box - cleanup access alarms and reset diagnostic
    * if alarm_policy disabled - cleanup access alarms
    * if alarm_policy enabled - raise access alarms
    :param profile_id:
    :return:
    """
    from noc.sa.models.managedobject import ManagedObject

    for (
        o_id,
        pool_id,
        fm_pool_id,
        diagnostics,
        enable_box_discovery,
        box_alarm,
        periodic_alarm,
        el,
    ) in (
        ManagedObject.objects.filter(is_managed=True, object_profile=profile_id)
        .filter(
            d_Q(diagnostics__CLI__state=DiagnosticState.failed.value)
            | d_Q(diagnostics__SNMP__state=DiagnosticState.failed.value)
            | d_Q(diagnostics__PROFILE__state=DiagnosticState.failed.value)
        )
        .values_list(
            "id",
            "pool",
            "fm_pool",
            "diagnostics",
            "object_profile__enable_box_discovery",
            "object_profile__box_discovery_alarm_policy",
            "object_profile__periodic_discovery_alarm_policy",
            "effective_labels",
        )
    ):
        fm_pool = fm_pool_id or pool_id
        fm_pool = Pool.get_by_id(fm_pool)
        o = GenericObject(
            id=o_id,
            object_profile=int(profile_id),
            diagnostics=diagnostics,
            pool=fm_pool.name,
            effective_labels=list(el),
        )
        with DiagnosticHub(o, dry_run=False) as d:
            d.sync_alarms(alarm_disable=box_alarm == "D" or not enable_box_discovery)


def apply_discovery_jobs(profile_id, box_changed, periodic_changed):
    def iter_objects():
        pool_cache = cachetools.LRUCache(maxsize=200)
        pool_cache.__missing__ = lambda x: Pool.objects.get(id=x)
        for o_id, is_managed, pool_id in profile.managedobject_set.values_list(
            "id", "is_managed", "pool"
        ):
            yield o_id, is_managed, pool_cache[pool_id]

    # No delete, fixed 'ManagedObjectProfile' object has no attribute 'managedobject_set'
    from .managedobject import ManagedObject  # noqa

    profile = ManagedObjectProfile.objects.filter(id=profile_id).first()
    if not profile:
        return
    for mo_id, is_managed, pool in iter_objects():
        shard, d_slots = None, config.get_slot_limits(f"discovery-{pool}")
        if d_slots:
            shard = mo_id % d_slots
        if box_changed:
            if profile.enable_box_discovery and is_managed:
                Job.submit(
                    "discovery",
                    "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    key=mo_id,
                    pool=pool,
                    shard=shard,
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
                    shard=shard,
                )
            else:
                Job.remove(
                    "discovery",
                    "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    key=mo_id,
                    pool=pool,
                )
