# ----------------------------------------------------------------------
# ManagedObject
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import difflib
import logging
import os
import re
import operator
from threading import Lock
import datetime
import warnings
from dataclasses import dataclass
from itertools import chain
from typing import Tuple, Iterable, List, Any, Dict, Set, Optional, Union

# Third-party modules
import cachetools
from django.contrib.postgres.fields import ArrayField
from django.db.models.query_utils import Q
from django.core.validators import MinValueValidator
from django.db.models import (
    CharField,
    BooleanField,
    ForeignKey,
    IntegerField,
    FloatField,
    BigIntegerField,
    SET_NULL,
    CASCADE,
    DateTimeField,
    When,
    Case,
    Value,
    Manager,
    Subquery,
    OuterRef,
)
from pydantic import BaseModel, RootModel
from pymongo import ASCENDING

# NOC modules
from noc.core.model.base import NOCModel
from noc.config import config
from noc.core.wf.diagnostic import (
    DiagnosticState,
    DiagnosticConfig,
    diagnostic,
    DIAGNOCSTIC_LABEL_SCOPE,
    SA_DIAG,
    ALARM_DIAG,
)
from noc.core.wf.interaction import Interaction
from noc.core.mx import (
    send_message,
    MessageType,
    MX_LABELS,
    MX_H_VALUE_SPLITTER,
    MX_ADMINISTRATIVE_DOMAIN_ID,
    MX_RESOURCE_GROUPS,
    MX_PROFILE_ID,
    MX_NOTIFICATION_DELAY,
)
from noc.core.deprecations import RemovedInNOC2301Warning
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.main.models.pool import Pool
from noc.main.models.timepattern import TimePattern
from noc.main.models.remotesystem import RemoteSystem
from noc.vc.models.l2domain import L2Domain
from noc.main.models.label import Label
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.profile import Profile
from noc.inv.models.capsitem import ModelCapsItem
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.firmwarepolicy import FirmwarePolicy
from noc.project.models.project import Project
from noc.fm.models.ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD
from noc.core.model.fields import (
    INETField,
    DocumentReferenceField,
    CachedForeignKey,
    ObjectIDArrayField,
    PydanticField,
)
from noc.core.model.sql import SQL
from noc.core.stencil import stencil_registry, Stencil
from noc.core.validators import is_ipv4, is_ipv4_prefix
from noc.core.ip import IP
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.gridvcs.manager import GridVCSField
from noc.main.models.textindex import full_text_search, TextIndex
from noc.core.scheduler.job import Job
from noc.main.models.handler import Handler
from noc.core.handler import get_handler
from noc.core.script.loader import loader as script_loader
from noc.core.model.decorator import (
    on_save,
    on_init,
    on_delete,
    on_delete_check,
    _get_field_snapshot,
)
from noc.inv.models.object import Object
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability
from noc.core.defer import call_later
from noc.core.cache.decorator import cachedmethod
from noc.core.cache.base import cache
from noc.core.script.caller import SessionContext, ScriptCaller
from noc.core.bi.decorator import bi_sync
from noc.core.script.scheme import (
    SCHEME_CHOICES,
    SNMPCredential,
    SNMPv3Credential,
    CLICredential,
    TELNET,
)
from noc.core.matcher import match
from noc.core.change.decorator import change, get_datastreams
from noc.core.change.policy import change_tracker
from noc.core.resourcegroup.decorator import resourcegroup
from noc.core.confdb.tokenizer.loader import loader as tokenizer_loader
from noc.core.confdb.engine.base import Engine
from noc.core.comp import smart_text, DEFAULT_ENCODING
from noc.main.models.glyph import Glyph
from noc.core.topology.types import (
    ShapeOverlayPosition,
    ShapeOverlayForm,
    ShapeOverlay,
    TopologyNode,
)
from noc.core.models.problem import ProblemItem
from noc.core.models.cfgmetrics import MetricCollectorConfig, MetricItem
from noc.core.wf.decorator import workflow
from noc.wf.models.state import State
from .administrativedomain import AdministrativeDomain
from .authprofile import AuthProfile
from .managedobjectprofile import ManagedObjectProfile
from .objectdiagnosticconfig import ObjectDiagnosticConfig

# Increase whenever new field added or removed
MANAGEDOBJECT_CACHE_VERSION = 51
CREDENTIAL_CACHE_VERSION = 7


@dataclass(frozen=True)
class Credentials(object):
    user: str
    password: str
    super_password: str
    snmp_ro: str
    snmp_rw: str
    snmp_rate_limit: str
    snmp_security_level: str
    snmp_username: str
    snmp_ctx_name: str
    snmp_auth_key: str
    snmp_auth_proto: str
    snmp_priv_key: str
    snmp_priv_proto: str
    snmp_rate_limit: int

    def get_snmp_credential(self) -> Optional[Union[SNMPCredential, SNMPv3Credential]]:
        if self.snmp_security_level == "Community" and self.snmp_ro:
            return SNMPCredential(snmp_ro=self.snmp_ro, snmp_rw=self.snmp_rw)
        elif self.snmp_security_level != "Community" and self.snmp_username:
            return SNMPv3Credential(
                username=self.snmp_username,
                auth_proto=self.snmp_auth_proto,
                auth_key=self.snmp_auth_key,
                private_proto=self.snmp_priv_proto,
                private_key=self.snmp_priv_key,
            )
        return None

    def get_cli_credential(self) -> Optional[CLICredential]:
        if not self.user:
            return None
        return CLICredential(
            username=self.user,
            password=self.password,
            super_password=self.super_password,
            raise_privilege=True,
        )


class MaintenanceItem(BaseModel):
    start: datetime.datetime
    # Time pattern when maintenance is active
    # None - active all the time
    time_pattern: Optional[int] = None
    stop: Optional[datetime.datetime] = None


MaintenanceItems = RootModel[Dict[str, MaintenanceItem]]


CapsItems = RootModel[List[ModelCapsItem]]


class MappingItem(BaseModel):
    remote_system: str
    remote_id: str


MappingItems = RootModel[List[MappingItem]]


class CheckStatus(BaseModel):
    name: str
    status: bool  # True - OK, False - Fail
    arg0: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None  # Description if Fail


class DiagnosticItem(BaseModel):
    diagnostic: str
    state: DiagnosticState = DiagnosticState("unknown")
    checks: Optional[List[CheckStatus]]
    # scope: Literal["access", "all", "discovery", "default"] = "default"
    # policy: str = "ANY
    reason: Optional[str] = None
    changed: Optional[datetime.datetime] = None

    def get_check_state(self):
        # Any policy
        return any(c.status for c in self.checks if not c.skipped)


DiagnosticItems = RootModel[Dict[str, DiagnosticItem]]


def default(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, datetime.datetime):
        return obj.replace(microsecond=0).isoformat(sep=" ")
    raise TypeError


@dataclass(frozen=True)
class ObjectUplinks(object):
    object_id: int
    uplinks: List[int]
    rca_neighbors: List[int]


id_lock = Lock()
e_labels_lock = Lock()

logger = logging.getLogger(__name__)


class ManagedObjectManager(Manager):
    """QuerySet manager for ManagedObject class to add non-database fields.

    A @property in the model cannot be used because QuerySets (eg. return
    value from .all()) are directly tied to the database Fields -
    this does not include @property attributes."""

    def get_queryset(self):
        """Overrides the models.Manager method"""
        # qs = super().get_queryset().annotate(cli_state=F("diagnostics__CLI__state"))
        qs = (
            super()
            .get_queryset()
            .annotate(
                avail_status=Subquery(
                    ManagedObjectStatus.objects.filter(managed_object=OuterRef("id")).values(
                        "status"
                    )
                ),
                is_managed=Case(
                    When(Q(diagnostics__SA__state="enabled"), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                has_sa=Case(
                    When(**{f"diagnostics__{SA_DIAG}__state": "blocked", "then": Value(False)}),
                    default=Value(True),
                    output_field=BooleanField(),
                ),
                has_alarm=Case(
                    When(**{f"diagnostics__{ALARM_DIAG}__state": "blocked", "then": Value(False)}),
                    default=Value(True),
                    output_field=BooleanField(),
                ),
            )
        )
        return qs


@full_text_search
@Label.dynamic_classification(
    profile_model_id="sa.ManagedObjectProfile", profile_field="object_profile"
)
@bi_sync
@on_init
@on_save
@on_delete
@workflow
@diagnostic
@change
@resourcegroup
@Label.model
@on_delete_check(
    check=[
        # ("cm.ValidationRule.ObjectItem", ""),
        ("fm.ActiveAlarm", "managed_object"),
        ("fm.ActiveEvent", "managed_object"),
        ("fm.ArchivedAlarm", "managed_object"),
        ("fm.ArchivedEvent", "managed_object"),
        ("fm.FailedEvent", "managed_object"),
        ("inv.Interface", "managed_object"),
        ("inv.SubInterface", "managed_object"),
        ("inv.ForwardingInstance", "managed_object"),
        ("sa.ManagedObject", "controller"),
        ("sla.SLAProbe", "managed_object"),
    ],
    delete=[
        ("sa.ManagedObjectAttribute", "managed_object"),
        ("sa.CPEStatus", "managed_object"),
        ("inv.CPE", "controllers__managed_object"),
        ("inv.MACDB", "managed_object"),
        ("sa.ServiceSummary", "managed_object"),
        ("inv.DiscoveryID", "object"),
        ("inv.Sensor", "managed_object"),
    ],
    clean=[
        ("ip.Address", "managed_object"),
        ("sa.Service", "managed_object"),
        ("maintenance.Maintenance", "escalate_managed_object"),
        ("maintenance.Maintenance", "direct_objects__object"),
        ("sa.DiscoveredObject", "managed_object"),
    ],
)
class ManagedObject(NOCModel):
    """
    Managed Object
    """

    class Meta(object):
        verbose_name = "Managed Object"
        verbose_name_plural = "Managed Objects"
        db_table = "sa_managedobject"
        app_label = "sa"

    name = CharField("Name", max_length=64, unique=True)
    container: "Object" = DocumentReferenceField(Object, null=True, blank=True)
    administrative_domain: "AdministrativeDomain" = CachedForeignKey(
        AdministrativeDomain, verbose_name="Administrative Domain", on_delete=CASCADE
    )
    segment: "NetworkSegment" = DocumentReferenceField(NetworkSegment, null=False, blank=False)
    pool: "Pool" = DocumentReferenceField(Pool, null=False, blank=False)
    project = CachedForeignKey(
        Project, verbose_name="Project", on_delete=CASCADE, null=True, blank=True
    )
    # Workflow
    state: "State" = DocumentReferenceField(State, null=True, blank=True)
    # Last state change
    state_changed = DateTimeField("State Changed", null=True, blank=True)
    # Timestamp expired
    expired = DateTimeField("Expired", null=True, blank=True)
    # Timestamp of last seen
    last_seen = DateTimeField("Last Seen", null=True, blank=True)
    # Timestamp of first discovery
    first_discovered = DateTimeField("First Discovered", null=True, blank=True)
    # Optional pool to route FM events
    fm_pool = DocumentReferenceField(Pool, null=True, blank=True)
    profile: "Profile" = DocumentReferenceField(
        Profile,
        null=False,
        blank=False,
        default=Profile.get_default_profile,
    )
    vendor: "Vendor" = DocumentReferenceField(Vendor, null=True, blank=True)
    platform: "Platform" = DocumentReferenceField(Platform, null=True, blank=True)
    version: "Firmware" = DocumentReferenceField(Firmware, null=True, blank=True)
    # Firmware version to upgrade
    # Empty, when upgrade not scheduled
    next_version = DocumentReferenceField(Firmware, null=True, blank=True)
    object_profile: "ManagedObjectProfile" = CachedForeignKey(
        ManagedObjectProfile, verbose_name="Object Profile", on_delete=CASCADE
    )
    description = CharField("Description", max_length=256, null=True, blank=True)
    # Access
    auth_profile: "AuthProfile" = CachedForeignKey(
        AuthProfile, verbose_name="Auth Profile", null=True, blank=True, on_delete=CASCADE
    )
    scheme = IntegerField("Scheme", choices=SCHEME_CHOICES)
    address = CharField("Address", max_length=64)
    port = IntegerField("Port", blank=True, null=True)
    user = CharField("User", max_length=32, blank=True, null=True)
    password = CharField("Password", max_length=32, blank=True, null=True)
    super_password = CharField("Super Password", max_length=32, blank=True, null=True)
    remote_path = CharField("Path", max_length=256, blank=True, null=True)
    trap_source_type = CharField(
        max_length=1,
        choices=[
            ("d", "Disable"),
            ("m", "Management Address"),
            ("s", "Specify address"),
            ("l", "Loopback address"),
            ("a", "All interface addresses"),
        ],
        default="m",
        null=False,
        blank=False,
    )
    trap_source_ip = INETField("Trap Source IP", null=True, blank=True, default=None)
    syslog_source_type = CharField(
        max_length=1,
        choices=[
            ("d", "Disable"),
            ("m", "Management Address"),
            ("s", "Specify address"),
            ("l", "Loopback address"),
            ("a", "All interface addresses"),
        ],
        default="m",
        null=False,
        blank=False,
    )
    syslog_source_ip = INETField("Syslog Source IP", null=True, blank=True, default=None)
    trap_community = CharField("Trap Community", blank=True, null=True, max_length=64)
    snmp_ro = CharField("RO Community", blank=True, null=True, max_length=64)
    snmp_rw = CharField("RW Community", blank=True, null=True, max_length=64)
    snmp_rate_limit: int = IntegerField(default=0)
    access_preference = CharField(
        "CLI Privilege Policy",
        max_length=8,
        choices=[
            ("P", "Profile"),
            ("S", "SNMP Only"),
            ("C", "CLI Only"),
            ("SC", "SNMP, CLI"),
            ("CS", "CLI, SNMP"),
        ],
        default="P",
    )
    # IPAM
    fqdn: str = CharField("FQDN", max_length=256, null=True, blank=True)
    address_resolution_policy = CharField(
        "Address Resolution Policy",
        choices=[("P", "Profile"), ("D", "Disabled"), ("O", "Once"), ("E", "Enabled")],
        max_length=1,
        null=False,
        blank=False,
        default="P",
    )
    #
    l2_domain = DocumentReferenceField(L2Domain, null=True, blank=True)
    # CM
    config = GridVCSField("config")
    # Default VRF
    vrf = ForeignKey("ip.VRF", verbose_name="VRF", blank=True, null=True, on_delete=CASCADE)
    # Reference to CPE
    cpe_id = DocumentReferenceField("inv.CPE", null=True, blank=True)
    # Reference to controller, when object is CPE
    controller = ForeignKey(
        "self", verbose_name="Controller", blank=True, null=True, on_delete=CASCADE
    )
    # Stencils
    shape = CharField(
        "Shape", blank=True, null=True, choices=stencil_registry.choices, max_length=128
    )
    shape_overlay_glyph = DocumentReferenceField(Glyph, null=True, blank=True)
    shape_overlay_position = CharField(
        "S.O. Position",
        max_length=2,
        choices=[(x.value, x.value) for x in ShapeOverlayPosition],
        null=True,
        blank=True,
    )
    shape_overlay_form = CharField(
        "S.O. Form",
        max_length=1,
        choices=[(x.value, x.value) for x in ShapeOverlayForm],
        null=True,
        blank=True,
    )
    shape_title_template = CharField("Shape Name template", max_length=256, blank=True, null=True)
    #
    time_pattern = ForeignKey(TimePattern, null=True, blank=True, on_delete=SET_NULL)
    # Config processing handlers
    config_filter_handler: "Handler" = DocumentReferenceField(Handler, null=True, blank=True)
    config_diff_filter_handler: "Handler" = DocumentReferenceField(Handler, null=True, blank=True)
    config_validation_handler: "Handler" = DocumentReferenceField(Handler, null=True, blank=True)
    #
    max_scripts = IntegerField(
        "Max. Scripts", null=True, blank=True, help_text="Concurrent script session limits"
    )
    # Latitude and longitude, copied from container
    x = FloatField(null=True, blank=True)
    y = FloatField(null=True, blank=True)
    default_zoom = IntegerField(null=True, blank=True)
    # Software characteristics
    software_image = CharField("Software Image", max_length=255, null=True, blank=True)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    mappings: Optional[List[MappingItem]] = PydanticField(
        "Remote System Mapping Items",
        schema=MappingItems,
        blank=True,
        null=True,
        default=list,
    )
    # Object id in remote system
    remote_id = CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = BigIntegerField(unique=True)
    # Object alarms can be escalated
    escalation_policy = CharField(
        "Escalation Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable"),
            ("P", "From Profile"),
            ("R", "Escalate as depended"),
        ],
        default="P",
    )
    # Discovery running policy
    box_discovery_running_policy = CharField(
        "Box Running Policy",
        choices=[
            ("P", "From Profile"),
            ("R", "Require Up"),
            ("r", "Require if enabled"),
            ("i", "Ignore"),
        ],
        max_length=1,
        default="P",
    )
    periodic_discovery_running_policy = CharField(
        "Periodic Running Policy",
        choices=[
            ("P", "From Profile"),
            ("R", "Require Up"),
            ("r", "Require if enabled"),
            ("i", "Ignore"),
        ],
        max_length=1,
        default="P",
    )
    # Raise alarms on discovery problems
    box_discovery_alarm_policy = CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
        default="P",
    )
    periodic_discovery_alarm_policy = CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
        default="P",
    )
    # Telemetry settings
    box_discovery_telemetry_policy = CharField(
        "Box Discovery Telemetry Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
        default="P",
    )
    box_discovery_telemetry_sample = IntegerField("Box Discovery Telemetry Sample", default=0)
    periodic_discovery_telemetry_policy = CharField(
        "Box Discovery Telemetry Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
        default="P",
    )
    periodic_discovery_telemetry_sample = IntegerField("Box Discovery Telemetry Sample", default=0)
    # TT system for this object
    tt_system: "TTSystem" = DocumentReferenceField(TTSystem, null=True, blank=True)
    # TT system queue for this object
    tt_queue = CharField(max_length=64, null=True, blank=True)
    # Object id in tt system
    tt_system_id = CharField(max_length=64, null=True, blank=True)
    # CLI session policy
    cli_session_policy = CharField(
        "CLI Session Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
        default="P",
    )
    # CLI privilege policy
    cli_privilege_policy = CharField(
        "CLI Privilege Policy",
        max_length=1,
        choices=[("E", "Raise privileges"), ("D", "Do not raise"), ("P", "From Profile")],
        default="P",
    )
    # Config policy
    config_policy = CharField(
        "Config Policy",
        max_length=1,
        choices=[
            ("P", "From Profile"),
            ("s", "Script"),
            ("S", "Script, Download"),
            ("D", "Download, Script"),
            ("d", "Download"),
        ],
        default="P",
    )
    config_fetch_policy = CharField(
        "Config Fetch Policy",
        max_length=1,
        choices=[("P", "From Profile"), ("s", "Startup"), ("r", "Running")],
        default="P",
    )
    # Interface discovery settings
    interface_discovery_policy = CharField(
        "Interface Discovery Policy",
        max_length=1,
        choices=[
            ("P", "From Profile"),
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="P",
    )
    # Caps discovery settings
    caps_discovery_policy = CharField(
        "Caps Discovery Policy",
        max_length=1,
        choices=[
            ("P", "From Profile"),
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="P",
    )
    # VLAN discovery settings
    vlan_discovery_policy = CharField(
        "VLAN Discovery Policy",
        max_length=1,
        choices=[
            ("P", "From Profile"),
            ("s", "Script"),
            ("S", "Script, ConfDB"),
            ("C", "ConfDB, Script"),
            ("c", "ConfDB"),
        ],
        default="P",
    )
    # Autosegmentation
    autosegmentation_policy = CharField(
        max_length=1,
        choices=[
            # Inherit from profile
            ("p", "Profile"),
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
        default="p",
    )
    #
    event_processing_policy = CharField(
        "Event Processing Policy",
        max_length=1,
        choices=[("P", "Profile"), ("E", "Process Events"), ("D", "Drop events")],
        default="P",
    )
    # Collect and archive syslog events
    syslog_archive_policy = CharField(
        "SYSLOG Archive Policy",
        max_length=1,
        choices=[("E", "Enable"), ("D", "Disable"), ("P", "Profile")],
        default="P",
    )
    # Behavior on denied firmware detection
    denied_firmware_policy = CharField(
        "Firmware Policy",
        max_length=1,
        choices=[
            ("P", "Profile"),
            ("I", "Ignore"),
            ("s", "Ignore&Stop"),
            ("A", "Raise Alarm"),
            ("S", "Raise Alarm&Stop"),
        ],
        default="P",
    )
    # ConfDB settings
    confdb_raw_policy = CharField(
        "ConfDB Raw Policy",
        max_length=1,
        choices=[("P", "Profile"), ("D", "Disable"), ("E", "Enable")],
        default="P",
    )
    # Dynamic Profile Classification
    dynamic_classification_policy = CharField(
        "Dynamic Classification Policy",
        max_length=1,
        choices=[("P", "Profile"), ("D", "Disable"), ("R", "By Rule")],
        default="P",
    )
    # Resource groups
    static_service_groups = ObjectIDArrayField(db_index=True, blank=True, null=True, default=list)
    effective_service_groups = ObjectIDArrayField(
        db_index=True, blank=True, null=True, default=list
    )
    static_client_groups = ObjectIDArrayField(db_index=True, blank=True, null=True, default=list)
    effective_client_groups = ObjectIDArrayField(db_index=True, blank=True, null=True, default=list)
    #
    labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(CharField(max_length=250), blank=True, null=True, default=list)
    #
    caps: List[Dict[str, Any]] = PydanticField(
        "Caps Items",
        schema=CapsItems,
        blank=True,
        null=True,
        default=list,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )
    # Additional data
    uplinks = ArrayField(IntegerField(), blank=True, null=True, default=list)
    links = ArrayField(IntegerField(), blank=True, null=True, default=list, db_index=True)
    # RCA neighbors cache
    rca_neighbors = ArrayField(IntegerField(), blank=True, null=True, default=list)
    # xRCA donwlink merge window settings
    # for rca_neighbors.
    # Each position represents downlink merge windows for each rca neighbor.
    # Windows are in seconds, 0 - downlink merge is disabled
    dlm_windows = ArrayField(IntegerField(), blank=True, null=True, default=list)
    # Paths
    adm_path = ArrayField(IntegerField(), blank=True, null=True, default=list)
    segment_path = ObjectIDArrayField(db_index=True, blank=True, null=True, default=list)
    container_path = ObjectIDArrayField(db_index=True, blank=True, null=True, default=list)
    affected_maintenances: Dict[str, Dict[str, str]] = PydanticField(
        "Maintenance Items",
        schema=MaintenanceItems,
        blank=True,
        null=True,
        default=dict,
        # ? Internal validation not worked with JSON Field
        # validators=[match_rules_validate],
    )
    diagnostics: Dict[str, DiagnosticItem] = PydanticField(
        "Diagnostic Items",
        schema=DiagnosticItems,
        blank=True,
        null=True,
        default=dict,
    )
    # Interval
    effective_metric_discovery_interval = IntegerField(default=0, validators=[MinValueValidator(0)])

    snmp_security_level = CharField(
        "SNMP protocol security",
        max_length=12,
        choices=[
            ("Community", "Community"),
            ("noAuthNoPriv", "noAuthNoPriv"),
            ("authNoPriv", "authNoPriv"),
            ("authPriv", "authPriv"),
        ],
        default="Community",
    )
    snmp_username = CharField("SNMP user name", max_length=32, null=True, blank=True)
    snmp_auth_proto = CharField(
        "Authentication protocol",
        max_length=3,
        choices=[("MD5", "MD5"), ("SHA", "SHA")],
        default="MD5",
    )
    snmp_auth_key = CharField("Authentication key", max_length=32, null=True, blank=True)
    snmp_priv_proto = CharField(
        "Privacy protocol",
        max_length=3,
        choices=[("DES", "DES"), ("AES", "AES")],
        default="DES",
    )
    snmp_priv_key = CharField("Privacy key", max_length=32, null=True, blank=True)
    snmp_ctx_name = CharField("Context name", max_length=32, null=True, blank=True)

    # Overridden objects manager
    objects = ManagedObjectManager()

    # Event ids
    EV_CONFIG_CHANGED = "config_changed"  # Object's config changed
    EV_ALARM_RISEN = "alarm_risen"  # New alarm risen
    EV_ALARM_REOPENED = "alarm_reopened"  # Alarm has been reopen
    EV_ALARM_CLEARED = "alarm_cleared"  # Alarm cleared
    EV_ALARM_COMMENTED = "alarm_commented"  # Alarm commented
    EV_NEW = "object_new"  # New object created
    EV_DELETED = "object_deleted"  # Object deleted
    EV_VERSION_CHANGED = "version_changed"  # Version changed
    EV_INTERFACE_CHANGED = "interface_changed"  # Interface configuration changed
    EV_SCRIPT_FAILED = "script_failed"  # Script error
    EV_CONFIG_POLICY_VIOLATION = "config_policy_violation"  # Policy violations found

    PROFILE_LINK = "object_profile"

    BOX_DISCOVERY_JOB = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
    PERIODIC_DISCOVERY_JOB = "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _mapping_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _e_labels_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _neighbor_cache = cachetools.TTLCache(1000, ttl=300)

    _ignore_on_save = (
        "caps",
        "uplinks",
        "links",
        "rca_neighbors",
        "dlm_windows",
        "adm_path",
        "segment_path",
        "container_path",
        "affected_maintenances",
        "diagnostics",
    )
    # Access affected fields
    _access_fields = {
        "scheme",
        "address",
        "port",
        "auth_profile",
        "object_profile",
        "user",
        "password",
        "super_password",
        "access_preference",
        "cli_privilege_policy",
    }

    def __str__(self):
        return self.name

    @classmethod
    @cachedmethod(
        operator.attrgetter("_id_cache"),
        key="managedobject-id-%s",
        lock=lambda _: id_lock,
        version=MANAGEDOBJECT_CACHE_VERSION,
    )
    def get_by_id(cls, id: int) -> Optional["ManagedObject"]:
        """
        Get ManagedObject by id. Cache returned instance for future use.

        :param oid: Managed Object's id
        :return: ManagedObject instance
        """
        return ManagedObject.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["ManagedObject"]:
        return ManagedObject.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_mapping_cache"), lock=lambda _: id_lock)
    def get_by_mapping(
        cls, remote_system: RemoteSystem, remote_id: str
    ) -> Optional["ManagedObject"]:
        return ManagedObject.objects.filter(
            Q(remote_system=str(remote_system.id), remote_id=remote_id)
            | Q(
                mappings__contains=[
                    {"remote_id": remote_id, "remote_system": str(remote_system.id)}
                ]
            )
        ).first()

    def iter_changed_datastream(self, changed_fields=None):
        changed_fields = set(changed_fields or [])
        if config.datastream.enable_managedobject:
            yield "managedobject", self.id
        if config.datastream.enable_cfgtarget:
            yield "cfgtarget", self.id
        if config.datastream.enable_cfgmetricsources and changed_fields.intersection(
            {"id", "bi_id", "state", "pool", "fm_pool", "labels", "effective_labels"}
        ):
            yield "cfgmetricsources", f"sa.ManagedObject::{self.bi_id}"

    def set_scripts_caller(self, caller):
        """
        Override default scripts caller
        :param caller: callabler
        :return:
        """
        self._scripts_caller = caller

    @property
    def scripts(self):
        sp = getattr(self, "_scripts", None)
        if sp:
            return sp
        self._scripts = ScriptsProxy(self, getattr(self, "_scripts_caller", None))
        return self._scripts

    @property
    def actions(self):
        return ActionsProxy(self)

    @property
    def matchers(self):
        mp = getattr(self, "_matchers", None)
        if mp:
            return mp
        self._matchers = MatchersProxy(self)
        return self._matchers

    def reset_matchers(self):
        self._matchers = None

    @classmethod
    def user_objects(cls, user):
        """
        Get objects available to user

        :param user: User
        :type user: User instance
        :rtype: Queryset instance
        """
        return cls.objects.filter(UserAccess.Q(user))

    def has_access(self, user):
        """
        Check user has access to object

        :param user: User
        :type user: User instance
        :rtype: Bool
        """
        if user.is_superuser:
            return True
        return self.user_objects(user).filter(id=self.id).exists()

    @property
    def granted_users(self):
        """
        Get list of user granted access to object

        :rtype: List of User instancies
        """
        return [
            u
            for u in User.objects.filter(is_active=True)
            if ManagedObject.objects.filter(UserAccess.Q(u) & Q(id=self.id)).exists()
        ]

    @property
    def granted_groups(self):
        """
        Get list of groups granted access to object

        :rtype: List of Group instancies
        """
        return [
            g
            for g in Group.objects.filter()
            if ManagedObject.objects.filter(GroupAccess.Q(g) & Q(id=self.id)).exists()
        ]

    @classmethod
    def get_component(
        cls, managed_object: "ManagedObject", mac=None, ipv4=None, vrf=None, **kwargs
    ) -> Optional["ManagedObject"]:
        from noc.inv.models.subinterface import SubInterface
        from noc.inv.models.forwardinginstance import ForwardingInstance
        from noc.inv.models.discoveryid import DiscoveryID

        if mac:
            mac = MACAddressParameter().clean(mac)
            return DiscoveryID.find_object(mac)
        if ipv4:
            q = {"ipv4_addresses": ipv4}
            if vrf is not None and vrf != "default":
                fi = list(ForwardingInstance.objects.filter(name=vrf)[:2])
                if len(fi) == 1:
                    q["forwarding_instance"] = fi[0]
            si = list(SubInterface.objects.filter(**q)[:2])
            if len(si) == 1:
                return si[0].managed_object

    def on_save(self):
        # Invalidate caches
        deleted_cache_keys = ["managedobject-name-to-id-%s" % self.name]
        diagnostics = []
        # Notify new object
        if not self.initial_data["id"]:
            self.event(self.EV_NEW)
        # Remove discovery jobs from old pool
        if "pool" in self.changed_fields and self.initial_data["id"]:
            pool_name = Pool.get_by_id(self.initial_data["pool"].id).name
            Job.remove("discovery", self.BOX_DISCOVERY_JOB, key=self.id, pool=pool_name)
            Job.remove("discovery", self.PERIODIC_DISCOVERY_JOB, key=self.id, pool=pool_name)
        # Reset matchers
        if (
            "vendor" in self.changed_fields
            or "platform" in self.changed_fields
            or "version" in self.changed_fields
            or "software_image" in self.changed_fields
        ):
            self.reset_matchers()
        # Invalidate credentials cache
        if (
            self.initial_data["id"] is None
            or self._access_fields.intersection(set(self.changed_fields))
            or "snmp_ro" in self.changed_fields
            or "snmp_rw" in self.changed_fields
            or "profile" in self.changed_fields
            or "vendor" in self.changed_fields
            or "platform" in self.changed_fields
            or "version" in self.changed_fields
            or "pool" in self.changed_fields
            or "remote_path" in self.changed_fields
            or "snmp_rate_limit" in self.changed_fields
        ):
            cache.delete("cred-%s" % self.id, version=CREDENTIAL_CACHE_VERSION)
        if self.initial_data["id"] is None or self._access_fields.intersection(
            set(self.changed_fields)
        ):
            diagnostics += ["CLI", "Access"]
        if (
            "auth_profile" in self.changed_fields
            or "snmp_ro" in self.changed_fields
            or "snmp_rw" in self.changed_fields
            or "address" in self.changed_fields
        ):
            diagnostics += ["SNMP", "Access"]
        # Rebuild paths
        if (
            self.initial_data["id"] is None
            or not self.adm_path
            or "administrative_domain" in self.changed_fields
            or "segment" in self.changed_fields
            or "container" in self.changed_fields
        ):
            self.adm_path = self.administrative_domain.get_path()
            self.segment_path = [str(sid) for sid in self.segment.get_path()]
            self.container_path = (
                [str(sid) for sid in self.container.get_path()] if self.container else []
            )
            ManagedObject.objects.filter(id=self.id).update(
                adm_path=self.adm_path,
                segment_path=self.segment_path,
                container_path=self.container_path,
            )
            if self.container and "container" in self.changed_fields:
                x, y, zoom = self.container.get_coordinates_zoom()
                ManagedObject.objects.filter(id=self.id).update(x=x, y=y, default_zoom=zoom)
        if self.initial_data["id"] and "container" in self.changed_fields:
            # Move object to another container
            if self.container:
                for o in Object.get_managed(self):
                    o.container = self.container.id
                    o.log("Moved to container %s (%s)" % (self.container, self.container.id))
                    o.save()
        # Rebuild summary
        if "object_profile" in self.changed_fields:
            NetworkSegment.update_summary(self.segment)
        # Apply discovery jobs
        self.ensure_discovery_jobs()
        #
        self._reset_caches(self.id, credential=True)
        cache.delete_many(deleted_cache_keys)
        # Rebuild segment access
        if self.initial_data["id"] is None:
            self.segment.update_access()
        elif "segment" in self.changed_fields:
            iseg = self.initial_data["segment"]
            if iseg and isinstance(iseg, str):
                iseg = NetworkSegment.get_by_id(iseg)
            if iseg:
                iseg.update_access()
            self.segment.update_access()
            self.update_topology()
            # Refresh links
            from noc.inv.models.link import Link

            for ll in Link.object_links(self):
                ll.save()
        # Handle became unmanaged
        if Interaction.Alarm not in self.interactions:
            # Clear alarms
            from noc.fm.models.activealarm import ActiveAlarm

            for aa in ActiveAlarm.objects.filter(managed_object=self.id):
                aa.clear_alarm("Management is disabled")
            # Clear discovery id
            from noc.inv.models.discoveryid import DiscoveryID

            DiscoveryID.clean_for_object(self)
        # Update configured state on diagnostics
        if diagnostics:
            # Reset changed diagnostic
            self.diagnostic.reset_diagnostics(diagnostics)
        elif "effective_labels" in self.changed_fields:
            # Update configured diagnostic
            self.diagnostic.refresh_diagnostics()
        # self.update_init()

    def on_delete(self):
        self._reset_caches(self.id, credential=True)
        self.event(self.EV_DELETED)

    def get_index(self):
        """
        Get FTS index
        """
        card = f"Managed object {self.name} ({self.address})"
        content: List[str] = [self.name, self.address]
        if self.trap_source_ip:
            content += [self.trap_source_ip]
        platform = self.platform
        if platform:
            content += [smart_text(platform.name)]
            card += " [%s]" % platform.name
        version = str(self.version)
        if version:
            content += [version]
            card += " version %s" % version
        if self.description:
            content += [self.description]
        config = self.config.read()
        if config:
            if len(config) > 10000000:
                content += [config[:10000000]]
            else:
                content += [config]
        r = {"title": self.name, "content": "\n".join(content), "card": card, "tags": self.labels}
        return r

    @classmethod
    def get_search_result_url(cls, obj_id):
        return "/api/card/view/managedobject/%s/" % obj_id

    @property
    def is_router(self):
        """
        Returns True if Managed Object presents in more than one networks
        :return:
        """
        # @todo: Rewrite
        return self.address_set.count() > 1

    def get_attr(self, name, default=None):
        """
        Return attribute as string
        :param name:
        :param default:
        :return:
        """
        warnings.warn(
            "Capability should be used instead of Attributes."
            " Will be strict requirement in NOC 23.1",
            RemovedInNOC2301Warning,
        )
        try:
            return self.managedobjectattribute_set.get(key=name).value
        except ManagedObjectAttribute.DoesNotExist:
            return default

    def get_attr_bool(self, name, default=False):
        """
        Return attribute as bool
        :param name:
        :param default:
        :return:
        """
        v = self.get_attr(name)
        if v is None:
            return default
        if v.lower() in ["t", "true", "y", "yes", "1"]:
            return True
        else:
            return False

    def get_attr_int(self, name, default=0):
        """
        Return attribute as integer
        :param name:
        :param default:
        :return:
        """
        v = self.get_attr(name)
        if v is None:
            return default
        try:
            return int(v)
        except:  # noqa
            return default

    def set_attr(self, name, value):
        """
        Set attribute
        :param name:
        :param value:
        :return:
        """
        value = smart_text(value)
        try:
            v = self.managedobjectattribute_set.get(key=name)
            v.value = value
        except ManagedObjectAttribute.DoesNotExist:
            v = ManagedObjectAttribute(managed_object=self, key=name, value=value)
        v.save()

    def update_attributes(self, attr):
        warnings.warn(
            "Capability should be used instead of Attributes."
            " Will be strict requirement in NOC 23.1",
            RemovedInNOC2301Warning,
        )
        for k in attr:
            v = attr[k]
            ov = self.get_attr(k)
            if ov != v:
                self.set_attr(k, v)
                logger.info("%s: %s -> %s", k, ov, v)

    def is_ignored_interface(self, interface):
        interface = self.get_profile().convert_interface_name(interface)
        rx = self.get_attr("ignored_interfaces")
        if rx:
            return re.match(rx, interface) is not None
        return False

    def get_status(self) -> bool:
        r = self.get_statuses([self.id])
        if self.id not in r:
            return True
        return r[self.id]

    def get_last_status(self):
        return ManagedObjectStatus.get_last_status(self)

    def set_status(self, status, ts=None):
        """
        Update managed object status
        :param status: new status
        :param ts: status change time
        :return: False if out-of-order update, True otherwise
        """
        return ManagedObjectStatus.set_status(self, status, ts=ts)

    @classmethod
    def get_statuses(cls, objects: List[int]) -> Dict[int, bool]:
        """
        Returns a map of object id -> status
        for a list od object ids
        """
        from django.db import connection as pg_connection

        s = {}
        with pg_connection.cursor() as cursor:
            while objects:
                chunk, objects = objects[:500], objects[500:]
                cursor.execute(
                    """
                    SELECT managed_object_id, status
                    FROM sa_objectstatus
                    WHERE managed_object_id = ANY(%s::INT[])
                    """,
                    [chunk],
                )
                for o, status in cursor:
                    s[o] = status
        return s

    def get_inventory(self):
        """
        Retuns a list of inventory Objects managed by
        this managed object
        """
        from noc.inv.models.object import Object

        return list(
            Object.objects.filter(
                data__match={"interface": "management", "attr": "managed_object", "value": self.id}
            )
        )

    def run_discovery(self, delta=0):
        """
        Schedule box discovery
        """
        if (
            not self.object_profile.enable_box_discovery
            or Interaction.BoxDiscovery not in self.interactions
        ):
            return
        logger.debug("[%s] Scheduling box discovery after %ds", self.name, delta)
        Job.submit(
            "discovery",
            self.BOX_DISCOVERY_JOB,
            key=self.id,
            pool=self.pool.name,
            delta=delta or self.pool.get_delta(),
        )

    def event(self, event_id: str, data: Optional[Dict[str, Any]] = None, delay=None, tag=None):
        """
        Process object-related event
        :param event_id: ManagedObject.EV_*
        :param data: Event context to render
        :param delay: Notification delay in seconds
        :param tag: Notification tag
        """
        logger.debug("[%s|%s] Sending object event message: %s", self.name, event_id, data)
        d = {"managed_object": self.get_message_context()}
        if data:
            d.update(data)
        headers = self.get_mx_message_headers([tag] if tag else None)
        if delay:
            headers[MX_NOTIFICATION_DELAY] = delay
        send_message(
            data=d,
            message_type=MessageType(event_id),
            headers=headers,
        )

        # Schedule FTS reindex
        if event_id in (self.EV_CONFIG_CHANGED, self.EV_VERSION_CHANGED):
            TextIndex.update_index(ManagedObject, self)

    def save_config(self, data, validate=True):
        """
        Save new configuration to GridVCS
        :param data: config
        :param validate: Run config validation
        :return: True if config has been changed, False otherwise
        """
        if isinstance(data, list):
            # Convert list to plain text
            r = []
            for d in sorted(data, key=operator.itemgetter("name")):
                r += [
                    "==[ %s ]========================================\n%s"
                    % (d["name"], d["config"])
                ]
            data = "\n".join(r)
        # Wipe out unnecessary parts
        if self.config_filter_handler:
            if self.config_filter_handler.allow_config_filter:
                handler = self.config_filter_handler.get_handler()
                data = handler(self, data) or ""
            else:
                logger.warning("Handler is not allowed for config filter")
        # Pass data through config filter, if given
        if self.config_diff_filter_handler:
            if self.config_diff_filter_handler.allow_config_diff_filter:
                handler = self.config_diff_filter_handler.get_handler()
                data = handler(self, data) or ""
            else:
                logger.warning("Handler is not allowed for config diff filter")
        # Pass data through the validation filter, if given
        # @todo: Replace with config validation policy
        if self.config_validation_handler:
            if self.config_validation_handler.allow_config_validation:
                handler = self.config_validation_handler.get_handler()
                warnings = handler(self, data)
                if warnings:
                    # There are some warnings. Notify responsible persons
                    self.event(self.EV_CONFIG_POLICY_VIOLATION, {"warnings": warnings})
            else:
                logger.warning("Handler is not allowed for config validation")
        # Calculate diff
        old_data = self.config.read()
        is_new = not bool(old_data)
        diff = None
        if is_new:
            changed = True
        else:
            # Calculate diff
            if self.config_diff_filter_handler:
                if self.config_diff_filter_handler.allow_config_diff_filter:
                    handler = self.config_diff_filter_handler.get_handler()
                    # Pass through filters
                    old_data = handler(self, old_data)
                    new_data = handler(self, data)
                    if not old_data and not new_data:
                        logger.error(
                            "[%s] broken config_diff_filter: Returns empty result", self.name
                        )
                else:
                    self.logger.warning("Handler is not allowed for config diff filter")
                    new_data = data
            else:
                new_data = data
            changed = old_data != new_data
            if changed:
                diff = "".join(
                    difflib.unified_diff(
                        old_data.splitlines(True),
                        new_data.splitlines(True),
                        fromfile=os.path.join("a", smart_text(self.name)),
                        tofile=os.path.join("b", smart_text(self.name)),
                    )
                )
        if changed:
            # Notify changes
            self.notify_config_changes(is_new=is_new, data=data, diff=diff)
            # Save config
            self.write_config(data)
        # Apply mirroring settings
        self.mirror_config(data, changed)
        # Apply changes if necessary
        if changed:
            change_tracker.register(
                "update",
                "sa.ManagedObject",
                str(self.id),
                fields=[],
                datastreams=get_datastreams(self),
            )
        return changed

    def notify_config_changes(self, is_new, data, diff):
        """
        Notify about config changes
        :param is_new:
        :param data:
        :param diff:
        :return:
        """
        self.event(self.EV_CONFIG_CHANGED, {"is_new": is_new, "config": data, "diff": diff})

    def write_config(self, data):
        """
        Save config to GridVCS
        :param data: Config data
        :return:
        """
        logger.debug("[%s] Writing config", self.name)
        self.config.write(data)

    def mirror_config(self, data, changed):
        """
        Save config to mirror
        :param data: Config data
        :param changed: True if config has been changed
        :return:
        """
        logger.debug("[%s] Mirroring config", self.name)
        policy = self.object_profile.config_mirror_policy
        # D - Disable
        if policy == "D":
            logger.debug("[%s] Mirroring is disabled by policy. Skipping", self.name)
            return
        # C - Mirror on Change
        if policy == "C" and not changed:
            logger.debug("[%s] Configuration has not been changed. Skipping", self.name)
            return
        # Check storage
        storage = self.object_profile.config_mirror_storage
        if not storage:
            logger.debug("[%s] Storage is not configured. Skipping", self.name)
            return
        if not storage.is_config_mirror:
            logger.debug(
                "[%s] Config mirroring is disabled for storage '%s'. Skipping",
                self.name,
                storage.name,
            )
            return  # No storage setting
        # Check template
        template = self.object_profile.config_mirror_template
        if not template:
            logger.debug("[%s] Path template is not configured. Skipping", self.name)
            return
        # Render path
        path = self.object_profile.config_mirror_template.render_subject(
            object=self, datetime=datetime
        ).strip()
        if not path:
            logger.debug("[%s] Empty mirror path. Skipping", self.name)
            return
        logger.debug(
            "[%s] Mirroring to %s:%s",
            self.name,
            self.object_profile.config_mirror_storage.name,
            path,
        )
        dir_path = os.path.dirname(path)
        try:
            with storage.open_fs() as fs:
                if dir_path and dir_path != "/" and not fs.isdir(dir_path):
                    logger.debug("[%s] Ensuring directory: %s", self.name, dir_path)
                    fs.makedirs(dir_path, recreate=True)
                logger.debug("[%s] Mirroring %d bytes", self.name, len(data))
                fs.writebytes(path, data.encode(encoding=DEFAULT_ENCODING))
        except storage.Error as e:
            logger.error("[%s] Failed to mirror config: %s", self.name, e)

    def to_validate(self, changed):
        """
        Check if config is to be validated

        :param changed: True if config has been changed
        :return: Boolean
        """
        policy = self.object_profile.config_validation_policy
        # D - Disable
        if policy == "D":
            logger.debug("[%s] Validation is disabled by policy. Skipping", self.name)
            return False
        # C - Validate on Change
        if policy == "C" and not changed:
            logger.debug("[%s] Configuration has not been changed. Skipping", self.name)
            return False
        return True

    def iter_validation_problems(self, changed: bool) -> Iterable[ProblemItem]:
        """
        Yield validation problems

        :param changed: True if config has been changed
        :return:
        """
        logger.debug("[%s] Validating config", self.name)
        if not self.to_validate(changed):
            return
        confdb = self.get_confdb()
        # Object-level validation
        if self.object_profile.object_validation_policy:
            yield from self.object_profile.object_validation_policy.iter_problems(confdb)
        else:
            logger.debug("[%s] Object validation policy is not set. Skipping", self.name)
        # Interface-level validation
        from noc.inv.models.interface import Interface
        from noc.inv.models.interfaceprofile import InterfaceProfile

        for doc in Interface._get_collection().aggregate(
            [
                {"$match": {"managed_object": self.id}},
                {"$project": {"_id": 0, "name": 1, "profile": 1}},
                {"$group": {"_id": "$profile", "ifaces": {"$push": "$name"}}},
            ]
        ):
            iprofile = InterfaceProfile.get_by_id(doc["_id"])
            if not iprofile or not iprofile.interface_validation_policy:
                continue
            for ifname in doc["ifaces"]:
                for problem in iprofile.interface_validation_policy.iter_problems(
                    confdb, ifname=ifname
                ):
                    yield problem

    @property
    def credentials(self) -> Credentials:
        """
        Get effective credentials
        """
        if self.auth_profile:
            return Credentials(
                user=self.auth_profile.user,
                password=self.auth_profile.password,
                super_password=self.auth_profile.super_password,
                snmp_ro=self.auth_profile.snmp_ro or self.snmp_ro,
                snmp_rw=self.auth_profile.snmp_rw or self.snmp_rw,
                snmp_rate_limit=self.get_effective_snmp_rate_limit(),
                snmp_security_level=self.auth_profile.snmp_security_level,
                snmp_username=self.auth_profile.snmp_username,
                snmp_ctx_name=self.auth_profile.snmp_ctx_name,
                snmp_auth_proto=self.auth_profile.snmp_auth_proto,
                snmp_auth_key=self.auth_profile.snmp_auth_key,
                snmp_priv_proto=self.auth_profile.snmp_priv_proto,
                snmp_priv_key=self.auth_profile.snmp_priv_key,
            )
        else:
            return Credentials(
                user=self.user,
                password=self.password,
                super_password=self.super_password,
                snmp_ro=self.snmp_ro,
                snmp_rw=self.snmp_rw,
                snmp_rate_limit=self.get_effective_snmp_rate_limit(),
                snmp_security_level=self.snmp_security_level,
                snmp_username=self.snmp_username,
                snmp_ctx_name=self.snmp_ctx_name,
                snmp_auth_proto=self.snmp_auth_proto,
                snmp_auth_key=self.snmp_auth_key,
                snmp_priv_proto=self.snmp_priv_proto,
                snmp_priv_key=self.snmp_priv_key,
            )

    @property
    def scripts_limit(self):
        ol = self.max_scripts or None
        pl = self.profile.max_scripts
        if not ol:
            return pl
        if pl:
            return min(ol, pl)
        else:
            return ol

    def iter_recursive_objects(self):
        """
        Generator yielding all recursive objects
        for effective PM settings
        """
        from noc.inv.models.interface import Interface

        yield from Interface.objects.filter(managed_object=self.id)

    def get_caps(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a dict of effective object capabilities
        """

        caps = {}
        scope = scope or ""
        if self.caps:
            for c in self.caps:
                cc = Capability.get_by_id(c["capability"])
                if not cc or (scope and c.get("scope", "") != scope):
                    continue
                caps[cc.name] = c.get("value")
        return caps

    def save(self, **kwargs):
        kwargs = kwargs or {}
        if getattr(self, "_allow_update_fields", None) and "update_fields" not in kwargs:
            kwargs["update_fields"] = self._allow_update_fields
        super().save(**kwargs)

    def update_caps(
        self, caps: Dict[str, Any], source: str, scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update existing capabilities with a new ones.
        :param caps: dict of caps name -> caps value
        :param source: Source name
        :param scope: Scope name
        """

        o_label = f"{scope or ''}|{self.name}|{source}"
        # Update existing capabilities
        new_caps = []
        seen = set()
        changed = False
        for ci in self.caps:
            c = Capability.get_by_id(ci["capability"])
            cs = ci.get("source")
            css = ci.get("scope", "")
            cv = ci.get("value")
            if not c:
                logger.info("[%s] Removing unknown capability id %s", o_label, ci["capability"])
                continue
            cv = c.clean_value(cv)
            cn = c.name
            seen.add(cn)
            if scope and scope != css:
                logger.debug(
                    "[%s] Not changing capability %s: from other scope '%s'",
                    o_label,
                    cn,
                    css,
                )
            elif cs == source:
                if cn in caps:
                    if caps[cn] != cv:
                        logger.info(
                            "[%s] Changing capability %s: %s -> %s", o_label, cn, cv, caps[cn]
                        )
                        ci["value"] = caps[cn]
                        changed = True
                else:
                    logger.info("[%s] Removing capability %s", o_label, cn)
                    changed = True
                    continue
            elif cn in caps:
                logger.info(
                    "[%s] Not changing capability %s: Already set with source '%s'",
                    o_label,
                    cn,
                    cs,
                )
            new_caps += [ci]
        # Add new capabilities
        for cn in set(caps) - seen:
            c = Capability.get_by_name(cn)
            if not c:
                logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
                continue
            logger.info("[%s] Adding capability %s = %s", o_label, cn, caps[cn])
            new_caps += [
                {"capability": str(c.id), "value": caps[cn], "source": source, "scope": scope or ""}
            ]
            changed = True

        if changed:
            logger.info("[%s] Saving changes", o_label)
            self.caps = new_caps
            ManagedObject.objects.filter(id=self.id).update(caps=self.caps)
            self.update_init()
            self._reset_caches(self.id, credential=True)
        caps = {}
        for ci in new_caps:
            cn = Capability.get_by_id(ci["capability"])
            if cn:
                caps[cn.name] = ci.get("value")
        return caps

    def set_caps(
        self, key: str, value: Any, source: str = "manual", scope: Optional[str] = ""
    ) -> None:
        caps = Capability.get_by_name(key)
        value = caps.clean_value(value)
        for item in self.caps:
            if item["capability"] == str(caps.id):
                if not scope or item.get("scope", "") == scope:
                    item["value"] = value
                    break
        else:
            # Insert new item
            self.caps += [
                {"capability": str(caps.id), "value": value, "source": source, "scope": scope or ""}
            ]
        ManagedObject.objects.filter(id=self.id).update(caps=self.caps)
        self.update_init()
        self._reset_caches(self.id, credential=True)

    def disable_discovery(self):
        """
        Disable all discovery methods related with managed object
        """

    def get_profile(self):
        """
        Getting profile methods
        Exa:
         mo.get_profile().convert_interface_name(i)
        :return:
        """
        profile = getattr(self, "_profile", None)
        if not profile:
            self._profile = self.profile.get_profile()
        return self._profile

    def get_interface(self, name):
        from noc.inv.models.interface import Interface

        name = self.get_profile().convert_interface_name(name)
        try:
            return Interface.objects.get(managed_object=self.id, name=name)
        except Interface.DoesNotExist:
            pass
        for n in self.get_profile().get_interface_names(name):
            try:
                return Interface.objects.get(managed_object=self.id, name=n)
            except Interface.DoesNotExist:
                pass
        return None

    def get_linecard(self, ifname):
        """
        Returns linecard number related to interface
        :param ifname:
        :return:
        """
        return self.get_profile().get_linecard(ifname)

    def ensure_discovery_jobs(self):
        """
        Check and schedule discovery jobs
        """
        shard, d_slots = None, config.get_slot_limits(f"discovery-{self.pool.name}")
        if d_slots:
            shard = self.id % d_slots
        if (
            Interaction.BoxDiscovery in self.interactions
            and self.object_profile.enable_box_discovery
        ):
            Job.submit(
                "discovery",
                self.BOX_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name,
                delta=self.pool.get_delta(),
                keep_ts=True,
                shard=shard,
            )
        else:
            Job.remove("discovery", self.BOX_DISCOVERY_JOB, key=self.id, pool=self.pool.name)
        if Interaction.PeriodicDiscovery in self.interactions and (
            self.object_profile.enable_periodic_discovery or self.object_profile.enable_metrics
        ):
            Job.submit(
                "discovery",
                self.PERIODIC_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name,
                delta=self.pool.get_delta(),
                keep_ts=True,
                shard=shard,
            )
        else:
            Job.remove("discovery", self.PERIODIC_DISCOVERY_JOB, key=self.id, pool=self.pool.name)

    def update_topology(self):
        """
        Rebuild topology caches
        """
        # Rebuild PoP links
        container = self.container
        for o in Object.get_managed(self):
            pop = o.get_pop()
            if not pop and container:
                # Fallback to MO container
                pop = container.get_pop()
            if pop:
                call_later("noc.inv.util.pop_links.update_pop_links", 20, pop_id=pop.id)

    @classmethod
    def get_search_Q(cls, query):
        """
        Filters type:
        #1 IP address regexp - if .* in query
        #2 Name regexp - if "+*[]()" in query
        #3 IPv4 query - if query is valid IPv4 address
        #4 IPv4 prefix - if query is valid prefix from /16 to /32 (192.168.0.0/16, 192.168.0.0/g, 192.168.0.0/-1)
        #5 Discovery ID query - Find on MAC Discovery ID
        :param query: Query from __query request field
        :return: Django Q filter (Use it: ManagedObject.objects.filter(q))
        """
        query = query.strip()
        if query:
            if ".*" in query and is_ipv4(query.replace(".*", ".1")):
                return Q(address__regex=query.replace(".", "\\.").replace("*", "[0-9]+"))
            elif set("+*[]()") & set(query):
                # Maybe regular expression
                try:
                    # Check syntax
                    # @todo: PostgreSQL syntax differs from python one
                    re.compile(query)
                    return Q(name__regex=query)
                except re.error:
                    pass
            elif is_ipv4(query):
                # Exact match on IP address
                return Q(address=query)
            elif is_ipv4_prefix(query):
                # Match by prefix
                p = IP.prefix(query)
                return SQL("cast_test_to_inet(address) <<= '%s'" % p)
            else:
                try:
                    mac = MACAddressParameter().clean(query)
                    from noc.inv.models.discoveryid import DiscoveryID

                    mo = DiscoveryID.find_all_objects(mac)
                    if mo:
                        return Q(id__in=mo)
                except ValueError:
                    pass
        return None

    def open_session(self, idle_timeout=None):
        return SessionContext(self, idle_timeout)

    def can_escalate(self, depended=False):
        """
        Check alarm can be escalated
        :return:
        """
        if not self.tt_system or not self.tt_system_id:
            return False
        return self.can_notify(depended)

    def can_notify(self, depended=False):
        """
        Check alarm can be notified via escalation
        :param depended:
        :return:
        """
        if self.escalation_policy == "E":
            return True
        elif self.escalation_policy == "P":
            return self.object_profile.can_escalate(depended)
        elif self.escalation_policy == "R":
            return bool(depended)
        else:
            return False

    def can_create_box_alarms(self):
        if self.box_discovery_alarm_policy == "E":
            return True
        elif self.box_discovery_alarm_policy == "P":
            return self.object_profile.can_create_box_alarms()
        else:
            return False

    def can_create_periodic_alarms(self):
        if self.periodic_discovery_alarm_policy == "E":
            return True
        elif self.periodic_discovery_alarm_policy == "P":
            return self.object_profile.can_create_periodic_alarms()
        else:
            return False

    def can_cli_session(self):
        if self.cli_session_policy == "E":
            return True
        elif self.cli_session_policy == "P":
            return self.object_profile.can_cli_session()
        else:
            return False

    @property
    def box_telemetry_sample(self):
        if self.box_discovery_telemetry_policy == "E":
            return self.box_discovery_telemetry_sample
        elif self.box_discovery_telemetry_policy == "P":
            return self.object_profile.box_discovery_telemetry_sample
        else:
            return 0

    @property
    def periodic_telemetry_sample(self):
        if self.periodic_discovery_telemetry_policy == "E":
            return self.periodic_discovery_telemetry_sample
        elif self.periodic_discovery_telemetry_policy == "P":
            return self.object_profile.periodic_discovery_telemetry_sample
        else:
            return 0

    @property
    def management_vlan(self):
        """
        Return management vlan settings
        :return: Vlan id or None
        """
        if self.segment.management_vlan_policy == "d":
            return None
        elif self.segment.management_vlan_policy == "e":
            return self.segment.management_vlan
        else:
            return self.segment.profile.management_vlan

    @property
    def multicast_vlan(self):
        """
        Return multicast vlan settings
        :return: Vlan id or None
        """
        if self.segment.multicast_vlan_policy == "d":
            return None
        elif self.segment.multicast_vlan_policy == "e":
            return self.segment.multicast_vlan
        else:
            return self.segment.profile.multicast_vlan

    @property
    def escalator_shard(self):
        """
        Returns escalator shard name
        :return:
        """
        if self.tt_system:
            return self.tt_system.shard_name
        else:
            return DEFAULT_TTSYSTEM_SHARD

    @property
    def to_raise_privileges(self):
        if self.cli_privilege_policy == "E":
            return True
        elif self.cli_privilege_policy == "P":
            return self.object_profile.cli_privilege_policy == "E"
        else:
            return False

    def get_autosegmentation_policy(self):
        if self.autosegmentation_policy == "p":
            return self.object_profile.autosegmentation_policy
        else:
            return self.autosegmentation_policy

    @property
    def enable_autosegmentation(self):
        return self.get_autosegmentation_policy() in ("o", "c")

    @property
    def allow_autosegmentation(self):
        return self.get_autosegmentation_policy() == "e"

    def get_access_preference(self):
        if self.access_preference != "P":
            return self.access_preference
        if self.version:
            fw_settings = self.version.get_effective_object_settings()
            return fw_settings.get("access_preference", self.object_profile.access_preference)
        return self.object_profile.access_preference

    def get_event_processing_policy(self):
        if self.event_processing_policy == "P":
            return self.object_profile.event_processing_policy
        else:
            return self.event_processing_policy

    def get_address_resolution_policy(self):
        if self.address_resolution_policy == "P":
            return self.object_profile.address_resolution_policy
        else:
            return self.address_resolution_policy

    def get_denied_firmware_policy(self):
        if self.denied_firmware_policy == "P":
            return self.object_profile.denied_firmware_policy
        return self.denied_firmware_policy

    def get_confdb_raw_policy(self):
        if self.confdb_raw_policy == "P":
            return self.object_profile.confdb_raw_policy
        return self.confdb_raw_policy

    def get_config_policy(self):
        if self.config_policy == "P":
            return self.object_profile.config_policy
        return self.config_policy

    def get_config_fetch_policy(self):
        if self.config_fetch_policy == "P":
            return self.object_profile.config_fetch_policy
        return self.config_fetch_policy

    def get_interface_discovery_policy(self):
        if self.interface_discovery_policy == "P":
            return self.object_profile.interface_discovery_policy
        return self.interface_discovery_policy

    def get_caps_discovery_policy(self):
        if self.caps_discovery_policy == "P":
            return self.object_profile.caps_discovery_policy
        return self.caps_discovery_policy

    def get_vlan_discovery_policy(self):
        if self.vlan_discovery_policy == "P":
            return self.object_profile.vlan_discovery_policy
        return self.vlan_discovery_policy

    def get_effective_box_discovery_running_policy(self):
        if self.box_discovery_running_policy == "P":
            return self.object_profile.box_discovery_running_policy
        return self.box_discovery_running_policy

    def get_effective_periodic_discovery_running_policy(self):
        if self.periodic_discovery_running_policy == "P":
            return self.object_profile.periodic_discovery_running_policy
        return self.periodic_discovery_running_policy

    def get_dynamic_classification_policy(self):
        if self.dynamic_classification_policy == "P":
            return self.object_profile.dynamic_classification_policy
        return self.dynamic_classification_policy

    def get_full_fqdn(self):
        if not self.fqdn:
            return None
        if self.fqdn.endswith(".") or not self.object_profile.fqdn_suffix:
            return self.fqdn[:-1]
        return f"{self.fqdn}.{self.object_profile.fqdn_suffix}"

    def resolve_fqdn(self):
        """
        Resolve FQDN to address
        :return:
        """
        fqdn = self.get_full_fqdn()
        if not fqdn:
            return None
        if self.object_profile.resolver_handler:
            handler = Handler.get_by_id(self.object_profile.resolver_handler)
            if handler and handler.allow_resolver:
                return handler.get_handler()(fqdn)
            elif handler and not handler.allow_resolver:
                logger.warning("Handler is not allowed for resolver")
                return None
        import socket

        try:
            return socket.gethostbyname(fqdn)
        except socket.gaierror:
            return None

    @classmethod
    def get_bi_selector(cls, cfg):
        qs = {}
        if "administrative_domain" in cfg:
            d = AdministrativeDomain.get_by_id(cfg["administrative_domain"])
            if d:
                qs["administrative_domain__in"] = d.get_nested()
        if "pool" in cfg:
            qs["pool__in"] = [cfg["pool"]]
        if "profile" in cfg:
            qs["profile__in"] = [cfg["profile"]]
        if "segment" in cfg:
            qs["segment__in"] = [cfg["segment"]]
        if "container" in cfg:
            qs["container__in"] = [cfg["container"]]
        if "vendor" in cfg:
            qs["vendor__in"] = [cfg["vendor"]]
        if "platform" in cfg:
            qs["platform__in"] = [cfg["platform"]]
        if "version" in cfg:
            qs["version__in"] = [cfg["version"]]
        return [int(r) for r in ManagedObject.objects.filter(**qs).values_list("bi_id", flat=True)]

    @property
    def metrics(self):
        metric, last = get_objects_metrics([self])
        return metric.get(self), last.get(self)

    def iter_config_tokens(self, config=None):
        if config is None:
            config = self.config.read()
        if not config:
            return  # no config
        t_name, t_config = self.profile.get_profile().get_config_tokenizer(self)
        if not t_name:
            return  # no tokenizer
        t_cls = tokenizer_loader.get_class(t_name)
        if not t_cls:
            raise ValueError("Invalid tokenizer")
        tokenizer = t_cls(config, **t_config)
        yield from tokenizer

    def iter_normalized_tokens(self, config=None):
        profile = self.profile.get_profile()
        n_handler, n_config = profile.get_config_normalizer(self)
        if not n_handler:
            return
        if not n_handler.startswith("noc."):
            n_handler = "noc.sa.profiles.%s.confdb.normalizer.%s" % (profile.name, n_handler)
        n_cls = get_handler(n_handler)
        if not n_cls:
            return
        normalizer = n_cls(self, self.iter_config_tokens(config), **n_config)
        yield from normalizer

    def get_confdb(self, config=None, cleanup=True):
        """
        Returns ready ConfDB engine instance

        :param config: Configuration data
        :param cleanup: Remove temporary nodes if True
        :return: confdb.Engine instance
        """
        profile = self.profile.get_profile()
        e = Engine()
        # Insert defaults
        defaults = profile.get_confdb_defaults(self)
        if defaults:
            e.insert_bulk(defaults)
        # Get working config
        if config is None:
            config = self.config.read()
        # Insert raw section
        if self.get_confdb_raw_policy() == "E":
            e.insert_bulk(("raw",) + t for t in self.iter_config_tokens(config))
        # Parse and normalize config
        e.insert_bulk(self.iter_normalized_tokens(config))
        # Apply applicators
        for applicator in profile.iter_config_applicators(self, e):
            applicator.apply()
        # Remove temporary nodes
        if cleanup:
            e.cleanup()
        return e

    @property
    def has_confdb_support(self):
        return self.profile.get_profile().has_confdb_support(self)

    @classmethod
    def mock_object(cls, profile=None):
        """
        Return mock object for tests

        :param profile: Profile name
        :return:
        """
        mo = ManagedObject()
        if profile:
            mo.profile = Profile.get_by_name(profile)
        mo.is_mock = True
        return mo

    def iter_technology(self, technologies):
        for o in Object.get_managed(self):
            yield from o.iter_technology(technologies)

    def get_effective_fm_pool(self):
        if self.fm_pool:
            return self.fm_pool
        return self.pool

    def get_effective_snmp_rate_limit(self) -> int:
        """
        Calculate effective SNMP rate limit
        :return:
        """
        if self.snmp_rate_limit > 0:
            return self.snmp_rate_limit
        if self.version:
            fw_settings = self.version.get_effective_object_settings()
            return fw_settings.get("snmp_rate_limit", self.object_profile.snmp_rate_limit)
        return self.object_profile.snmp_rate_limit

    @classmethod
    def _reset_caches(cls, mo_id: int, credential: bool = False):
        try:
            del cls._id_cache[f"managedobject-id-{mo_id}"]
        except KeyError:
            pass
        try:
            del cls._e_labels_cache[mo_id]
        except KeyError:
            pass
        cache.delete(f"managedobject-id-{mo_id}", version=MANAGEDOBJECT_CACHE_VERSION)
        if credential:
            cache.delete(f"cred-{mo_id}", version=CREDENTIAL_CACHE_VERSION)

    @property
    def events_stream_and_partition(self) -> Tuple[str, int]:
        """
        Return publish stream and partition for events
        :return: stream name, partition
        """
        fm_pool = self.get_effective_fm_pool().name
        slots = config.get_slot_limits(f"classifier-{fm_pool}") or 1
        return f"events.{fm_pool}", self.id % slots

    @property
    def alarms_stream_and_partition(self) -> Tuple[str, int]:
        """
        Return publish stream and partition for alarms
        :return: stream name, partition
        """
        fm_pool = self.get_effective_fm_pool().name
        slots = config.get_slot_limits(f"correlator-{fm_pool}") or 1
        return f"dispose.{fm_pool}", self.id % slots

    @cachetools.cached(_e_labels_cache, key=lambda x: str(x.id), lock=e_labels_lock)
    def get_effective_labels(self) -> List[str]:
        return Label.merge_labels(ManagedObject.iter_effective_labels(self))

    @classmethod
    def iter_effective_labels(cls, instance: "ManagedObject") -> Iterable[List[str]]:
        yield list(instance.labels or [])
        yield list(instance.object_profile.labels or [])
        if instance.state:
            yield list(instance.state.labels)
        else:
            # When create
            yield ["noc::is_managed::="]
        yield list(AdministrativeDomain.iter_lazy_labels(instance.administrative_domain))
        yield list(Pool.iter_lazy_labels(instance.pool))
        yield list(ManagedObjectProfile.iter_lazy_labels(instance.object_profile))
        if instance.effective_service_groups:
            yield ResourceGroup.get_lazy_labels(instance.effective_service_groups)
        yield Label.get_effective_regex_labels("managedobject_name", instance.name)
        lazy_profile_labels = list(Profile.iter_lazy_labels(instance.profile))
        yield Label.ensure_labels(lazy_profile_labels, ["sa.ManagedObject"])
        if instance.vendor:
            lazy_vendor_labels = list(Vendor.iter_lazy_labels(instance.vendor))
            yield Label.ensure_labels(lazy_vendor_labels, ["sa.ManagedObject"])
        if instance.platform:
            lazy_platform_labels = list(Platform.iter_lazy_labels(instance.platform))
            yield Label.ensure_labels(lazy_platform_labels, ["sa.ManagedObject"])
        if instance.address:
            yield Label.get_effective_prefixfilter_labels("managedobject_address", instance.address)
            yield Label.get_effective_regex_labels("managedobject_address", instance.address)
        if instance.description:
            yield Label.get_effective_regex_labels(
                "managedobject_description", instance.description
            )
        if instance.vrf:
            yield list(VRF.iter_lazy_labels(instance.vrf))
        if instance.tt_system:
            yield list(TTSystem.iter_lazy_labels(instance.tt_system))
        if instance.version:
            ep = FirmwarePolicy.get_effective_policies(instance.version, instance.platform)
            if ep:
                yield from [e.effective_labels for e in ep if e.effective_labels]
        if instance.links:
            # If use Link.objects.filter(linked_objects=mo.id).first() - 1.27 ms,
            # Interface = 39.4 µs
            yield ["noc::is_linked::="]
        if instance.diagnostics:
            for d in instance.diagnostic:
                yield Label.ensure_labels(
                    [f"{DIAGNOCSTIC_LABEL_SCOPE}::{d.diagnostic}::{d.state}"],
                    ["sa.ManagedObject"],
                )

    @classmethod
    def can_set_label(cls, label: str) -> bool:
        return Label.get_effective_setting(label, "enable_managedobject")

    @classmethod
    def uplinks_for_objects(cls, objects: List["ManagedObject"]) -> Dict[int, List[int]]:
        """
        Returns uplinks for list of objects
        :param objects: List of object
        :return: dict of object id -> uplinks
        """
        o = []
        for obj in objects:
            if hasattr(obj, "id"):
                obj = obj.id
            o += [obj]
        uplinks = {obj: [] for obj in o}
        for oid, mo_uplinks in ManagedObject.objects.filter(id__in=o).values_list("id", "uplinks"):
            uplinks[oid] = mo_uplinks or []
        return uplinks

    @classmethod
    def update_uplinks(cls, iter_uplinks: Iterable[ObjectUplinks]) -> None:
        """
        Update ObjectUplinks in database
        :param iter_uplinks: Iterable of ObjectUplinks
        :return:
        """
        from django.db import connection as pg_connection
        from noc.core.change.model import ChangeField

        obj_data: List[ObjectUplinks] = []
        seen_neighbors: Set[int] = set()
        uplinks: Dict[int, Set[int]] = {}
        for ou in iter_uplinks:
            obj_data += [ou]
            seen_neighbors |= set(ou.rca_neighbors)
            uplinks[ou.object_id] = set(ou.uplinks)
        if not obj_data:
            return  # No uplinks for segment
        # Get downlink_merge window settings
        dlm_settings: Dict[int, int] = {}
        if seen_neighbors:
            with pg_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT mo.id, mop.enable_rca_downlink_merge, mop.rca_downlink_merge_window
                    FROM sa_managedobject mo JOIN sa_managedobjectprofile mop
                        ON mo.object_profile_id = mop.id
                    WHERE mo.id IN %s""",
                    [tuple(seen_neighbors)],
                )
                dlm_settings = {mo_id: dlm_w for mo_id, is_enabled, dlm_w in cursor if is_enabled}
        # Propagate downlink-merge settings downwards
        dlm_windows: Dict[int, int] = {}
        MAX_WINDOW = 1000000
        for o in seen_neighbors:
            ups = uplinks.get(o)
            if not ups:
                continue
            w = min(dlm_settings.get(u, MAX_WINDOW) for u in ups)
            if w == MAX_WINDOW:
                w = 0
            dlm_windows[o] = w
        # Prepare bulk update operation
        for ou in obj_data:
            # mo: "ManagedObject" = ManagedObject.get_by_id(ou.object_id)
            ManagedObject.objects.filter(id=ou.object_id).update(
                uplinks=ou.uplinks,
                rca_neighbors=ou.rca_neighbors,
                dlm_windows=[dlm_windows.get(o, 0) for o in ou.rca_neighbors],
            )
            ManagedObject._reset_caches(ou.object_id)
            change_tracker.register(
                "update",
                "sa.ManagedObject",
                str(ou.object_id),
                fields=[
                    ChangeField(field="uplinks", new=ou.uplinks),
                    ChangeField(field="rca_neighbors", new=ou.rca_neighbors),
                ],
                datastreams=[("managedobject", ou.object_id)],
            )

    @classmethod
    def update_links(cls, linked_objects: List[int], exclude_link_ids: List[str] = None) -> None:
        """

        :param linked_objects:
        :param exclude_link_ids: Exclude link ID from update
        :return:
        """
        from noc.inv.models.link import Link
        from django.db import connection as pg_connection

        coll = Link._get_collection()
        r: Dict[int, Set] = {lo: set() for lo in linked_objects}
        match_expr = {"linked_objects": {"$in": linked_objects}}
        if exclude_link_ids:
            match_expr["_id"] = {"$nin": exclude_link_ids}
        # Check ManagedObject Link Count
        for c in coll.aggregate(
            [
                {"$match": match_expr},
                {"$project": {"neighbors": "$linked_objects", "linked_objects": 1}},
                {"$unwind": "$linked_objects"},
                {"$group": {"_id": "$linked_objects", "neighbors": {"$push": "$neighbors"}}},
            ]
        ):
            if c["_id"] not in r:
                continue
            r[c["_id"]] = set(chain(*c["neighbors"])) - {c["_id"]}
        # Update ManagedObject links
        for lo in r:
            if r[lo]:
                # Add Links
                SQL = """
                    UPDATE sa_managedobject
                    SET effective_labels = CASE WHEN 'noc::is_linked::=' = ANY(effective_labels)
                        THEN effective_labels ELSE effective_labels || '{"noc::is_linked::="}' END,
                        links = %s::numeric[]
                    WHERE id = %s;
                    """
            else:
                # Remove Links
                SQL = """
                    UPDATE sa_managedobject
                    SET effective_labels = CASE WHEN 'noc::is_linked::=' = ANY(effective_labels)
                        THEN array_remove(effective_labels, 'noc::is_linked::=') ELSE effective_labels END,
                        links = %s::numeric[]
                    WHERE id = %s;
                    """
            with pg_connection.cursor() as cursor:
                cursor.execute(SQL, [list(r[lo]), lo])
                # Generate change
            ManagedObject._reset_caches(lo)

    @property
    def in_maintenance(self) -> bool:
        """
        Check device is under active maintenance
        :return:
        """
        return any(self.get_active_maintenances())

    def get_active_maintenances(self, timestamp: Optional[datetime.datetime] = None) -> List[str]:
        """
        Getting device active maintenances ids
        :param timestamp:
        :return:
        """
        timestamp = timestamp or datetime.datetime.now()
        r = []
        for mai_id, d in self.affected_maintenances.items():
            if d.get("time_pattern"):
                # Restrict to time pattern
                tp = TimePattern.get_by_id(d["time_pattern"])
                if tp and not tp.match(timestamp):
                    continue
            if datetime.datetime.fromisoformat(d["start"]) > timestamp:
                continue
            if d.get("stop") and datetime.datetime.fromisoformat(d["stop"]) < timestamp:
                # Already complete
                continue
            r.append(mai_id)
        return r

    def get_message_context(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "administrative_domain": {
                "id": str(self.profile.id),
                "name": self.administrative_domain.name,
            },
            "profile": {"id": str(self.profile.id), "name": self.profile.name},
            "object_profile": {"id": str(self.object_profile.id), "name": self.object_profile.name},
        }

    def iter_diagnostic_configs(self) -> Iterable[DiagnosticConfig]:
        """
        Iterate over object diagnostics
        :return:
        """
        yield from self.state.iter_diagnostic_configs(self)
        yield from self.object_profile.iter_diagnostic_configs(self)
        for dc in ObjectDiagnosticConfig.iter_object_diagnostics(self):
            yield dc

    def update_init(self):
        """
        Update initial_data field
        :return:
        """
        self.initial_data = _get_field_snapshot(self.__class__, self)

    def iter_collected_metrics(
        self, run: int = 0, d_interval: Optional[int] = None
    ) -> Iterable[MetricCollectorConfig]:
        """
        Return metrics setting for collected by box or periodic
        :param run:
        :return:
        """
        if Interaction.ServiceActivation not in self.interactions:
            return
        from noc.inv.models.cpe import CPE
        from noc.sla.models.slaprobe import SLAProbe
        from noc.inv.models.interface import Interface
        from noc.inv.models.sensor import Sensor

        metrics: List[MetricItem] = []
        d_interval = d_interval or self.get_metric_discovery_interval()
        for mc in ManagedObjectProfile.get_object_profile_metrics(self.object_profile.id).values():
            interval = mc.interval or self.object_profile.metrics_default_interval
            mi = MetricItem(
                name=mc.metric_type.name,
                field_name=mc.metric_type.field_name,
                scope_name=mc.metric_type.scope.table_name,
                is_stored=mc.is_stored,
                is_compose=mc.metric_type.is_compose,
                interval=interval,
            )
            if interval and mi.is_run(d_interval, int(self.bi_id), 1, run):
                metrics.append(mi)
        cpe = None
        if self.cpe_id:
            cpe = CPE.get_by_id(self.cpe_id)
        if metrics:
            logger.debug("Object metrics: %s", ",".join(m.name for m in metrics))
            yield MetricCollectorConfig(
                collector="managed_object", metrics=tuple(metrics), cpe=cpe.bi_id if cpe else None
            )
        yield from CPE.iter_collected_metrics(self, run=run, d_interval=d_interval)
        yield from SLAProbe.iter_collected_metrics(self, run=run, d_interval=d_interval)
        yield from Interface.iter_collected_metrics(self, run=run, d_interval=d_interval)
        yield from Sensor.iter_collected_metrics(self, run=run, d_interval=d_interval)

    @classmethod
    def get_metric_config(cls, mo: "ManagedObject"):
        """
        Return MetricConfig for Metrics service
        :param mo:
        :return:
        """
        from noc.inv.models.interface import Interface
        from noc.inv.models.interfaceprofile import InterfaceProfile
        from noc.pm.models.metricrule import MetricRule

        if Interaction.ServiceActivation not in mo.interactions:
            return {}
        icoll = Interface._get_collection()
        s_metrics = mo.object_profile.get_object_profile_metrics(mo.object_profile.id)
        labels = []
        for ll in sorted(mo.effective_labels):
            l_c = Label.get_by_name(ll)
            labels.append({"label": ll, "expose_metric": l_c.expose_metric if l_c else False})
        items = []
        for iface in icoll.find(
            {"managed_object": mo.id}, {"name", "effective_labels", "profile"}
        ).sort([("name", ASCENDING)]):
            ip = InterfaceProfile.get_by_id(iface["profile"])
            metrics = [
                {
                    "name": mc.metric_type.field_name,
                    "is_stored": mc.is_stored,
                    "is_composed": bool(mc.metric_type.compose_expression),
                }
                for mc in ip.metrics
            ]
            if not metrics:
                continue
            items.append(
                {
                    "key_labels": [f"noc::interface::{iface['name']}"],
                    "labels": [],
                    "rules": [
                        ma for ma in MetricRule.iter_rules_actions(iface["effective_labels"])
                    ],
                    "metrics": metrics,
                }
            )
        return {
            "type": "managed_object",
            "bi_id": mo.bi_id,
            "fm_pool": mo.get_effective_fm_pool().name,
            "labels": labels,
            "discovery_interval": mo.get_metric_discovery_interval(),
            "metrics": [
                {
                    "name": mc.metric_type.field_name,
                    "is_stored": mc.is_stored,
                    "is_composed": bool(mc.metric_type.compose_expression),
                }
                for mc in s_metrics.values()
            ],
            "rules": [ma for ma in MetricRule.iter_rules_actions(mo.effective_labels)],
            "items": items,
            "sharding_key": mo.bi_id,
            "meta": mo.get_message_context(),
        }

    @property
    def has_configured_metrics(self) -> bool:
        """
        Check configured collected metrics
        :return:
        """
        if Interaction.ServiceActivation not in self.interactions:
            return False
        if not self.object_profile.enable_metrics:
            return False
        return bool(self.get_metric_discovery_interval())

    def get_stencil(self) -> Optional[Stencil]:
        if self.shape:
            # Use mo's shape, if set
            return self.shape
        if self.object_profile.shape:
            # Use profile's shape
            return self.object_profile.shape
        return

    def get_shape_overlays(self) -> List[ShapeOverlay]:
        seen: Set[ShapeOverlayPosition] = set()
        r: List[ShapeOverlay] = []
        # ManagedObject
        if self.shape_overlay_glyph:
            pos = self.shape_overlay_position or ShapeOverlayPosition.NW
            r += [
                ShapeOverlay(
                    code=self.shape_overlay_glyph.code,
                    position=pos,
                    form=self.shape_overlay_form or ShapeOverlayForm.Circle,
                )
            ]
            seen.add(pos)
        # Project
        if self.project and self.project.shape_overlay_glyph:
            pos = self.project.shape_overlay_position or ShapeOverlayPosition.NW
            if pos not in seen:
                r += [
                    ShapeOverlay(
                        code=self.project.shape_overlay_glyph.code,
                        position=pos,
                        form=self.project.shape_overlay_form or ShapeOverlayForm.Circle,
                    )
                ]
                seen.add(pos)
        # ManagedObjectProfile
        if self.object_profile.shape_overlay_glyph:
            pos = self.object_profile.shape_overlay_position or ShapeOverlayPosition.NW
            if pos not in seen:
                r += [
                    ShapeOverlay(
                        code=self.object_profile.shape_overlay_glyph.code,
                        position=pos,
                        form=self.object_profile.shape_overlay_form or ShapeOverlayForm.Circle,
                    )
                ]
                seen.add(pos)
        return r

    def get_topology_node(self) -> TopologyNode:
        return TopologyNode(
            id=str(self.id),
            type="managedobject",
            resource_id=self.id,
            title=self.name,
            title_metric_template=self.shape_title_template
            or self.object_profile.shape_title_template
            or "",
            stencil=self.get_stencil(),
            overlays=self.get_shape_overlays(),
            level=self.object_profile.level,
            attrs={"address": self.address, "mo": self},
        )

    def get_metric_discovery_interval(self) -> int:
        """
        Return Metric Discovery interval by MetricConfigs
        :return:
        """
        from noc.inv.models.cpe import CPE
        from noc.sla.models.slaprobe import SLAProbe
        from noc.inv.models.interface import Interface
        from noc.inv.models.sensor import Sensor

        r = [self.object_profile.get_metric_discovery_interval()]
        caps = self.get_caps()
        for caps_count, source in [
            ("DB | CPEs", CPE),
            ("DB | SLAProbes", SLAProbe),
            ("DB | Interfaces", Interface),
            ("DB | Sensors", Sensor),
        ]:
            count = caps.get(caps_count)
            if not count:
                continue
            interval = source.get_metric_discovery_interval(self)
            if interval:
                r += [interval]
        return max(min(r), config.discovery.min_metric_interval)

    @property
    def interactions(self) -> "InteractionHub":
        interactions = getattr(self, "_features", None)
        if interactions:
            return interactions
        self._interactions = InteractionHub(self)
        return self._interactions

    def get_mx_message_headers(self, labels: Optional[List[str]] = None) -> Dict[str, bytes]:
        return {
            MX_LABELS: MX_H_VALUE_SPLITTER.join(self.effective_labels + (labels or [])).encode(
                DEFAULT_ENCODING
            ),
            MX_ADMINISTRATIVE_DOMAIN_ID: str(self.administrative_domain.id).encode(
                DEFAULT_ENCODING
            ),
            MX_PROFILE_ID: str(self.object_profile.id).encode(DEFAULT_ENCODING),
            MX_RESOURCE_GROUPS: MX_H_VALUE_SPLITTER.join(
                [str(sg) for sg in self.effective_service_groups]
            ).encode(DEFAULT_ENCODING),
        }

    def set_mapping(self, remote_system: RemoteSystem, remote_id: str):
        """
        Set Object mapping
        Args:
            remote_system: Remote System Instance
            remote_id: Id on Remote system
        """
        rid = str(remote_system.id)
        for m in self.mappings:
            if m["remote_system"] == rid and m["remote_id"] != remote_id:
                m["remote_id"] = remote_id
                break
            elif m["remote_system"] == rid:
                break
        else:
            self.mappings += [{"remote_system": rid, "remote_id": remote_id}]

    def get_mapping(self, remote_system: RemoteSystem) -> Optional[str]:
        """return object mapping from"""
        for m in self.mappings:
            if m["remote_system"] == str(remote_system.id):
                return m["remote_id"]
        return None

    @classmethod
    def get_object_by_template(
        cls,
        address: str,
        pool: str,
        name: Optional[str] = None,
        template=None,
        **data,
    ) -> "ManagedObject":
        mo = ManagedObject(
            name=name or address,
            address=address,
            pool=pool,
            description=data.get("description"),
            scheme=TELNET,
            object_profile=ManagedObjectProfile.objects.filter().first(),
            administrative_domain=AdministrativeDomain.objects.filter().first(),
            segment=NetworkSegment.objects.filter().first(),
        )
        return mo

    def update_template_data(self, data, template=None): ...


@on_save
class ManagedObjectAttribute(NOCModel):
    class Meta(object):
        verbose_name = "Managed Object Attribute"
        verbose_name_plural = "Managed Object Attributes"
        db_table = "sa_managedobjectattribute"
        app_label = "sa"
        unique_together = [("managed_object", "key")]
        ordering = ["managed_object", "key"]

    managed_object = ForeignKey(ManagedObject, verbose_name="Managed Object", on_delete=CASCADE)
    key = CharField("Key", max_length=64)
    value = CharField("Value", max_length=4096, blank=True, null=True)

    def __str__(self):
        return "%s: %s" % (self.managed_object, self.key)

    def on_save(self):
        cache.delete(f"cred-{self.managed_object.id}", version=CREDENTIAL_CACHE_VERSION)


@on_save
class ManagedObjectStatus(NOCModel):
    class Meta(object):
        verbose_name = "Managed Object Status"
        verbose_name_plural = "Managed Object Status"
        db_table = "sa_objectstatus"
        app_label = "sa"

    managed_object = ForeignKey(
        ManagedObject, verbose_name="Managed Object", on_delete=CASCADE, unique=True
    )
    status = BooleanField()
    last = DateTimeField("Last update Time", auto_now_add=True)

    def __str__(self):
        return "%s: %s" % (self.managed_object, self.status)

    @classmethod
    def get_last_status(cls, o) -> Tuple[Optional[bool], Optional[datetime.datetime]]:
        """
        Returns last registered status and update time
        :param o: Managed Object
        :return: last status, last update or None
        """
        from django.db import connection as pg_connection

        with pg_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT status, last
                FROM sa_objectstatus
                WHERE managed_object_id = %s
                """,
                [o.id],
            )
            r = cursor.fetchone()
            if r:
                return r
        return None, None

    @classmethod
    def set_status(cls, object, status, ts=None):
        """
        Update object status
        :param object: Managed Object instance
        :param status: New status
        :param ts: Status change timestamp
        :return: True, if status has been changed, False - out-of-order update
        """
        cls.update_status_bulk([(object.id, status, ts)])

    @classmethod
    def update_status_bulk(
        cls,
        statuses: List[Tuple[int, bool, Optional[datetime.datetime]]],
        update_jobs: bool = False,
    ):
        """
        Update statuses bulk
        :param statuses:
        :param update_jobs:
        :return:
        """
        from django.db import connection as pg_connection
        from collections import defaultdict
        from psycopg2.extras import execute_values
        from noc.core.service.loader import get_service
        from noc.core.scheduler.scheduler import Scheduler

        now = datetime.datetime.now()
        bulk = {}
        outages: List[Tuple[int, datetime.datetime, datetime.datetime]] = []
        # Getting current status
        cs = {}
        with pg_connection.cursor() as cursor:
            cursor.execute(
                # """
                # SELECT managed_object_id, status, last, mo.pool
                # FROM sa_objectstatus
                # LEFT JOIN sa_managedobject AS mo ON sa_objectstatus.managed_object_id = mo.id
                # WHERE managed_object_id = ANY(%s::INT[])
                # """,
                """
                SELECT id, os.status, os.last, mo.pool
                FROM sa_managedobject AS mo
                LEFT JOIN sa_objectstatus AS os ON mo.id = os.managed_object_id
                WHERE id = ANY(%s::INT[])
                """,
                [[x[0] for x in statuses]],
            )
            for o, status, last, pool in cursor:
                pool = Pool.get_by_id(pool)
                cs[o] = {"status": status, "last": last, "pool": pool.name}
        # Processed new statuses
        suspended_jobs = defaultdict(list)  # Pool - ids
        for oid, status, ts in statuses:
            if oid not in cs:
                logger.error("Unknown object id: %s", oid)
                continue
            ts = (ts or now).replace(microsecond=0, tzinfo=None)
            if cs[oid]["status"] is None or (cs[oid]["status"] != status and cs[oid]["last"] <= ts):
                bulk[oid] = (oid, status, ts)  # Only last status
                if update_jobs:
                    suspended_jobs[(cs[oid]["pool"], status)].append(oid)
                # Update job timestamp to next, Add when outage was closed (device up)
                if cs[oid]["last"] and status:
                    outages.append((oid, cs[oid]["last"], ts))
                cs[oid].update({"status": status, "last": ts})
            elif cs[oid]["last"] > ts:
                # Oops, out-of-order update
                # Restore correct state
                pass
        if not bulk:
            return
        # Save statuses to db
        with pg_connection.cursor() as cursor:
            execute_values(
                cursor,
                """
                INSERT INTO sa_objectstatus as os (managed_object_id, status, last) VALUES %s
                ON CONFLICT (managed_object_id) DO UPDATE SET status = EXCLUDED.status, last = EXCLUDED.last
                WHERE os.status != EXCLUDED.status and os.last < EXCLUDED.last
                """,
                list(bulk.values()),
                page_size=500,
            )
        svc = get_service()
        # Send outages
        for out in outages:
            # Sent outages
            oid, start, stop = out
            mo = ManagedObject.get_by_id(oid)
            svc.register_metrics(
                "outages",
                [
                    {
                        "date": now.date().isoformat(),
                        "ts": now.replace(microsecond=0).isoformat(),
                        "managed_object": mo.bi_id,
                        "start": start.replace(microsecond=0).isoformat(),
                        "stop": stop.replace(microsecond=0).isoformat(),
                        "administrative_domain": mo.administrative_domain.bi_id,
                    }
                ],
                key=mo.bi_id,
            )
        for (pool, status), keys in suspended_jobs.items():
            sc = Scheduler("discovery", pool=pool)
            sc.suspend_keys(keys, suspend=not status)


# object.scripts. ...
class ScriptsProxy(object):
    def __init__(self, obj, caller=None):
        self._object = obj
        self._cache = {}
        self._caller = caller or ScriptCaller

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]
        if not script_loader.has_script("%s.%s" % (self._object.profile.name, name)):
            raise AttributeError("Invalid script %s" % name)
        cw = self._caller(self._object, name)
        self._cache[name] = cw
        return cw

    def __getitem__(self, item):
        return getattr(self, item)

    def __contains__(self, item):
        """
        Check object has script name
        """
        if "." not in item:
            # Normalize to full name
            item = "%s.%s" % (self._object.profile.name, item)
        return script_loader.has_script(item)

    def __iter__(self):
        prefix = self._object.profile.name + "."
        return (x.split(".")[-1] for x in script_loader.iter_scripts() if x.startswith(prefix))


class ActionsProxy(object):
    class CallWrapper(object):
        def __init__(self, obj, name, action):
            self.name = name
            self.object = obj
            self.action = action

        def __call__(self, **kwargs):
            return self.action.execute(self.object, **kwargs)

    def __init__(self, obj):
        self._object = obj
        self._cache = {}

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]
        a = Action.objects.filter(name=name).first()
        if not a:
            raise AttributeError(name)
        cw = ActionsProxy.CallWrapper(self._object, name, a)
        self._cache[name] = cw
        return cw


class MatchersProxy(object):
    def __init__(self, obj):
        self._object = obj
        self._data = None

    def _rebuild(self):
        # Build version structure
        version = {}
        if self._object.vendor:
            version["verndor"] = self._object.vendor.code
        if self._object.platform:
            version["platform"] = self._object.platform.name
        if self._object.version:
            version["version"] = self._object.version.version
        if self._object.software_image:
            version["image"] = self._object.software_image
        # Compile matchers
        matchers = self._object.get_profile().matchers
        self._data = {m: match(version, matchers[m]) for m in matchers}

    def __getattr__(self, name):
        if self._data is None:
            # Rebuild matchers
            self._rebuild()
        return self._data[name]

    def __contains__(self, item):
        if self._data is None:
            self._rebuild()
        return item in self._data


class InteractionHub(object):
    """
    Return available interaction on object
    If interaction is not supported - return None
    If interaction is supported - return enabled/disabled
    """

    def __init__(self, obj):
        self.logger = logging.getLogger(__name__)
        self.__supported_interactions: Set[Interaction] = self.load_supported_interactions()
        self.__state: State = obj.state or obj.workflow.get_default_state()

    @staticmethod
    def load_supported_interactions():
        return set(i for i in Interaction if "sa.ManagedObject" in i.config.models)

    def __getattr__(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        if name not in self.__supported_interactions:
            return None
        return self.__state.is_enabled_interaction(name)

    def __contains__(self, interaction: Union[str, Interaction]) -> bool:
        if interaction not in self.__supported_interactions:
            return False
        return self.__state.is_enabled_interaction(interaction)


# Avoid circular references
from .useraccess import UserAccess
from .groupaccess import GroupAccess
from .action import Action
from noc.core.pm.utils import get_objects_metrics
from noc.ip.models.vrf import VRF
