# ----------------------------------------------------------------------
# ManagedObject DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from collections import defaultdict
from typing import Optional, Iterable, Dict, Any, List, Tuple, AsyncIterable

# Third-party modules
import polars as pl
from django.db.models.expressions import Case, When, Value
from django.db.models.fields import BooleanField
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.profile import Profile
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.inv.models.capability import Capability
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.discoveryid import DiscoveryID
from noc.project.models.project import Project
from noc.core.validators import is_objectid
from noc.core.wf.diagnostic import (
    DiagnosticState,
    SNMP_DIAG,
    CLI_DIAG,
    PROFILE_DIAG,
    SYSLOG_DIAG,
    SNMPTRAP_DIAG,
)

caps_dtype_map = {
    "bool": FieldType.BOOL,
    "str": FieldType.STRING,
    "int": FieldType.UINT,
    "float": FieldType.FLOAT,
}


def iter_capabilities() -> Iterable[Tuple[str, str]]:
    for key, c_type, value in (
        Capability.objects.filter().order_by("name").scalar("id", "type", "name")
    ):
        yield key, caps_dtype_map[c_type], value


def get_adm_path_level() -> int:
    return 3


class ManagedObjectDS(BaseDataSource):
    name = "managedobjectds"
    row_index = "managed_object_id"
    params = [
        ParamInfo(name="pool", type="str", model="main.Pool"),
        ParamInfo(name="ids", type="int", allow_multi=True),
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
    ]

    fields = (
        [
            FieldInfo(name="id", description="Object Id", type=FieldType.UINT),
            FieldInfo(
                name="managed_object_id",
                description="Object Id",
                internal_name="id",
                type=FieldType.UINT,
            ),
            FieldInfo(name="name", description="Object Name"),
            FieldInfo(name="profile", description="Profile Name"),
            FieldInfo(name="pool", description="Pool Name"),
            FieldInfo(
                name="object_profile",
                description="Object Profile Name",
                internal_name="object_profile__name",
            ),
            FieldInfo(name="hostname", description="Object Hostname", internal_name="id"),
            FieldInfo(
                name="status",
                description="Object Admin Status",
                type=FieldType.BOOL,
                internal_name="is_managed",
            ),
            FieldInfo(name="address", description="Object IP Address"),
            # Inventory fields
            FieldInfo(name="vendor", description="Object Vendor"),
            FieldInfo(name="model", description="Object Model", internal_name="platform"),
            FieldInfo(name="sw_version", description="Object Firmware", internal_name="version"),
            # Attributes fields
            FieldInfo(
                name="attr_hwversion",
                description="Object HW Version Attribute",
                internal_name="Chassis | HW Version",
                is_caps=True,
            ),
            FieldInfo(
                name="attr_bootprom",
                description="Object Boot Prom Attribute",
                internal_name="Chassis | Boot PROM",
                is_caps=True,
            ),
            FieldInfo(
                name="attr_patch",
                description="Object Patch Attribute",
                internal_name="Software | Patch Version",
                is_caps=True,
            ),
            FieldInfo(
                name="attr_serialnumber",
                description="Object Serial Number Attribute",
                internal_name="Chassis | Serial Number",
                is_caps=True,
            ),
            FieldInfo(
                name="adm_path",
                description="Object Adm path",
                internal_name="administrative_domain__name",
                is_virtual=True,
            ),
            FieldInfo(
                name="caps",
                description="Object Capabilities",
                is_virtual=True,
            ),
            FieldInfo(
                name="chassis_macs",
                description="Macs",
                internal_name="id",
            ),
            FieldInfo(
                name="mappings",
                description="Object Mappings",
                is_virtual=True,
            ),
            # Location Fields
            FieldInfo(
                name="administrativedomain",
                description="Object Administrative Domain",
                internal_name="administrative_domain__name",
            ),
            FieldInfo(
                name="container",
                description="Object Container Name",
            ),
            FieldInfo(
                name="segment",
                description="Object Segment Name",
            ),
            FieldInfo(
                name="project",
                description="Object Segment Name",
            ),
            FieldInfo(
                name="auth_profile",
                description="Object Authentication Profile",
            ),
            # Stat fields
            FieldInfo(
                name="link_count",
                description="Object links count",
                internal_name="links",
                type=FieldType.UINT,
            ),
            FieldInfo(
                name="object_labels",
                description="Object Labels",
                internal_name="labels",
                type=FieldType.LIST_STRING,
            ),
            FieldInfo(
                name="physical_iface_count",
                description="Object physical interfaces",
                internal_name="DB | Interfaces",
                type=FieldType.UINT,
                is_caps=True,
            ),
            # Oper fields
            FieldInfo(
                name="avail",
                description="Object Availability Status",
                internal_name="avail_status",
            ),
            # Discovery enabled fields
            FieldInfo(
                name="enable_box",
                type=FieldType.BOOL,
                description="Enable Box Discovery",
                internal_name="object_profile__enable_box_discovery",
            ),
            FieldInfo(
                name="enable_periodic",
                type=FieldType.BOOL,
                description="Enable Periodic Discovery",
                internal_name="object_profile__enable_periodic_discovery",
            ),
            FieldInfo(
                name="enable_metrics",
                type=FieldType.BOOL,
                description="Enable Metric Discovery",
                internal_name="object_profile__enable_metrics",
            ),
            FieldInfo(
                name="enable_ping",
                type=FieldType.BOOL,
                description="Enable Availability check by Ping",
                internal_name="object_profile__enable_ping",
            ),
            FieldInfo(
                name="enable_topology",
                type=FieldType.BOOL,
                description="Enable Device Topology check",
                internal_name="object_profile__enable_box_discovery_lldp",
            ),
            # Troubles
            FieldInfo(
                name="trouble_snmp",
                type=FieldType.BOOL,
                description="SNMP is OK (SNMP Diagnostic not in failed state",
                is_diagnostic_state=DiagnosticState.failed,
                internal_name=SNMP_DIAG,
            ),
            FieldInfo(
                name="trouble_profile",
                type=FieldType.BOOL,
                description="Profile is OK (SNMP Diagnostic not in failed state",
                is_diagnostic_state=DiagnosticState.failed,
                internal_name=PROFILE_DIAG,
            ),
            FieldInfo(
                name="trouble_cli",
                type=FieldType.BOOL,
                description="CLI is OK (SNMP Diagnostic not in failed state",
                is_diagnostic_state=DiagnosticState.failed,
                internal_name=CLI_DIAG,
            ),
            FieldInfo(
                name="trouble_detail",
                description="Trouble detail message",
                internal_name="diagnostics",
            ),
            FieldInfo(
                name="recv_syslog",
                type=FieldType.BOOL,
                description="SNMP Trap is received",
                is_diagnostic_state=DiagnosticState.enabled,
                internal_name=SYSLOG_DIAG,
            ),
            FieldInfo(
                name="recv_snmptrap",
                type=FieldType.BOOL,
                description="SNMP Trap is received",
                is_diagnostic_state=DiagnosticState.enabled,
                internal_name=SNMPTRAP_DIAG,
            ),
        ]
        # Remote System
        + [
            FieldInfo(name=f"RS_{rs.name}", internal_name=str(rs.id))
            for rs in RemoteSystem.objects.filter()
        ]
        # Capabilities
        + [
            FieldInfo(
                name=c_name, type=c_type, internal_name=str(c_id), is_caps=True, is_vector=True
            )
            for c_id, c_type, c_name in iter_capabilities()
        ]
        + [
            FieldInfo(
                name=f"adm_path_{level}",
                internal_name="administrative_domain__name",
                is_vector=True,
            )
            for level in range(1, get_adm_path_level() + 1)
        ]
    )

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pl.DataFrame:
        """
        Method for query report data. Return pandas dataframe.
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """
        if "detail_query" in kwargs:
            print("Detail Query execute", kwargs["detail_query"])
            r = await super().query(fields=None, *args, **kwargs)
            sql = pl.SQLContext()
            sql.register("mo", r.lazy())
            return sql.execute(kwargs["detail_query"], eager=True).select(fields or [])
        return await super().query(fields=fields, *args, **kwargs)

    @classmethod
    async def iter_caps(
        cls, caps: List[Dict[str, Any]], requested_caps: Dict[str, Any] = None
    ) -> AsyncIterable[Tuple[str, Any]]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.

        :param caps:
        :param requested_caps:
        :return:
        """
        caps = {c["capability"]: c["value"] for c in caps}
        for cid, fields in requested_caps.items():
            for f_name, f_default in fields:
                yield f_name, caps.get(cid, f_default)

    @classmethod
    async def iter_mappings(
        cls, mappings: List[Dict[str, Any]], requested_mappings: Dict[str, str] = None
    ) -> AsyncIterable[Tuple[str, Any]]:
        mappings = {c["remote_system"]: c["remote_id"] for c in mappings}
        for rid, r_name in requested_mappings.items():
            yield r_name, mappings.get(rid, "")

    @staticmethod
    def get_caps_default(caps: Capability):
        """
        Capability field default value
        :param caps:
        :return:
        """
        if caps.type == "str":
            return ""
        elif caps.type == "int":
            return 0
        elif caps.type == "float":
            return 0.0
        return False

    @staticmethod
    def load_adm_path() -> Dict[str, Tuple[str, str]]:
        from django.db import connection as pg_connection

        with pg_connection.cursor() as cursor:
            cursor.execute(
                """
            SELECT ad.id, ad.name, r.name, ad2.name
            FROM sa_administrativedomain r
            JOIN sa_administrativedomain ad ON ad.parent_id = r.id
            JOIN sa_administrativedomain ad2 ON r.parent_id = ad2.id;
            """
            )
            return {r[1]: (r[2], r[3]) for r in cursor}

    @classmethod
    async def get_json(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs):
        return [mm async for mm in cls.iter_row(fields, *args, **kwargs)]

    @staticmethod
    def get_filter(filters: Dict[str, Any]) -> Dict[str, Any]:
        from noc.inv.models.resourcegroup import ResourceGroup

        r = {}
        if "pool" in filters:
            r["pool"] = str(filters["pool"].id)
        if "ids" in filters:
            r["id__in"] = [int(x) for x in filters["ids"]]
        if "resource_group" in filters:
            r["effective_service_groups__overlap"] = ResourceGroup.get_nested_ids(
                filters["resource_group"],
                convert_oid=True,
            )
        if "segment" in filters:
            r["segment__in"] = filters["segment"].get_nested_ids()
        return r

    @staticmethod
    def get_diagnostic_trouble(
        diagnostics: Dict[str, Any],
        snmp: bool = False,
        profile: bool = False,
        cli: bool = False,
    ) -> str:
        if snmp:
            x = [SNMP_DIAG]
        elif cli:
            x = [CLI_DIAG]
        elif profile:
            x = [PROFILE_DIAG]
        else:
            x = [SNMP_DIAG, PROFILE_DIAG, CLI_DIAG]
        for d in x:
            if d in diagnostics and diagnostics[d]["state"] == DiagnosticState.failed.value:
                for c in diagnostics[d]["checks"] or []:
                    if c["error"]:
                        return c["error"]
        return ""

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        user=None,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        fields = set(fields or [])
        q_fields, q_caps, q_maps = [], defaultdict(list), {}
        adm_paths = {}
        annotations = {}
        # Getting requested fields
        for f in cls.fields:
            f_query_name = f.internal_name or f.name
            if f_query_name in q_fields:
                continue
            if f.is_caps and (not fields or "caps" in fields or f.name in fields):
                if is_objectid(f.internal_name):
                    c = Capability.get_by_id(f.internal_name)
                else:
                    c = Capability.get_by_name(f.internal_name)
                if not c:
                    continue
                q_caps[str(c.id)] += [(f.name, cls.get_caps_default(c))]
            elif f.is_diagnostic_state:
                annotations[f.name] = Case(
                    When(
                        **{
                            f"diagnostics__{f.internal_name}__state": f.is_diagnostic_state,
                            "then": Value(True),
                        }
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
                q_fields.append(f.name)
            elif f.name.startswith("RS") and f.internal_name:
                q_maps[f.internal_name] = f.name
            elif not fields or f.name in fields or f.name == "id":
                q_fields.append(f_query_name)
        if q_caps and "caps" not in q_fields:
            q_fields.append("caps")
        if q_maps:
            q_fields.append("mappings")
        q_filter = cls.get_filter(kwargs)
        mos = ManagedObject.objects.filter(**q_filter)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        # Annotation
        if annotations:
            mos = mos.annotate(**annotations)
        # Dictionaries
        hostname_map, segment_map, mac_map = {}, {}, {}
        # Lookup fields dictionaries
        if not fields or "hostname" in fields:
            for val in (
                DiscoveryID._get_collection()
                .with_options(
                    read_preference=ReadPreference.SECONDARY_PREFERRED,
                )
                .find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1, "chassis_mac": 1})
            ):
                hostname_map[val["object"]] = val["hostname"]
                if "chassis_mac" in val:
                    mac_map[val["object"]] = ",".join(m["first_mac"] for m in val["chassis_mac"])
        if not fields or "segment" in fields:
            segment_map = {
                str(n["_id"]): n["name"]
                for n in NetworkSegment._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({}, {"name": 1})
            }
        if not fields or "adm_path" in fields:
            adm_paths = cls.load_adm_path()
        for num, mo in enumerate(mos.values(*q_fields).iterator(), start=1):
            yield num, "id", mo["id"]
            yield num, "managed_object_id", mo["id"]
            if "name" in mo:
                yield num, "name", mo["name"]
            if "address" in mo:
                yield num, "address", mo["address"]
            if "is_managed" in mo:
                yield num, "status", mo["is_managed"]
            if "links" in mo:
                yield num, "link_count", len(mo["links"])
            if "profile" in mo:
                yield num, "profile", (
                    Profile.get_by_id(mo["profile"]).name if mo["profile"] else None
                )
            if "pool" in mo:
                yield num, "pool", Pool.get_by_id(mo["pool"]).name if mo["pool"] else None
            if "platform" in mo:
                platform = mo["platform"]
                yield num, "model", Platform.get_by_id(platform).name if platform else None
            if "version" in mo:
                sw_version = mo["version"]
                yield num, "sw_version", (
                    Firmware.get_by_id(sw_version).version if sw_version else None
                )
            if "vendor" in mo:
                yield num, "vendor", Vendor.get_by_id(mo["vendor"]).name if mo["vendor"] else None
            if hostname_map:
                yield num, "hostname", hostname_map.get(mo["id"])
            if mac_map:
                yield num, "chassis_macs", mac_map.get(mo["id"])
            if segment_map:
                yield num, "segment", segment_map.get(mo["segment"])
            if "avail_status" in mo:
                yield num, "avail", {None: "--", True: "yes", False: "no"}[mo["avail_status"]]
            if "auth_profile" in mo:
                yield num, "auth_profile", (
                    AuthProfile.get_by_id(mo["auth_profile"]).name if mo["auth_profile"] else None
                )
            if "administrative_domain__name" in mo:
                yield num, "administrativedomain", mo["administrative_domain__name"]
            if "object_profile__name" in mo:
                yield num, "object_profile", mo["object_profile__name"]
            if "project" in mo:
                yield num, "project", (
                    Project.get_by_id(mo["project"]).name if mo["project"] else None
                )
            if "labels" in mo:
                yield num, "object_labels", mo["labels"]
            if "container" in mo:
                yield num, "container", ""
            # Discovery
            if "object_profile__enable_box_discovery" in mo:
                yield num, "enable_box", mo["object_profile__enable_box_discovery"]
            if "object_profile__enable_periodic_discovery" in mo:
                yield num, "enable_periodic", mo["object_profile__enable_periodic_discovery"]
            if "object_profile__enable_metrics" in mo:
                yield num, "enable_metrics", mo["object_profile__enable_metrics"]
            if "object_profile__enable_ping" in mo:
                yield num, "enable_ping", mo["object_profile__enable_ping"]
            #
            if "trouble_snmp" in mo:
                yield num, "trouble_snmp", mo["trouble_snmp"]
            if "trouble_profile" in mo:
                yield num, "trouble_profile", mo["trouble_profile"]
            if "trouble_cli" in mo:
                yield num, "trouble_cli", mo["trouble_cli"]
            if "recv_syslog" in mo:
                yield num, "recv_syslog", mo["recv_syslog"]
            if "recv_snmptrap" in mo:
                yield num, "recv_snmptrap", mo["recv_snmptrap"]
            if "diagnostics" in mo:
                yield num, "trouble_detail", cls.get_diagnostic_trouble(
                    mo["diagnostics"],
                    mo["trouble_snmp"],
                    mo["trouble_profile"],
                    mo["trouble_cli"],
                )
            async for c in cls.iter_caps(mo.pop("caps", []), requested_caps=q_caps):
                yield num, c[0], c[1]
            if not fields or "mappings" in fields:
                async for c in cls.iter_mappings(mo.pop("mappings", []), requested_mappings=q_maps):
                    yield num, c[0], c[1]
            if adm_paths and "administrative_domain__name" in mo:
                adm_name = mo["administrative_domain__name"]
                yield num, "adm_path_1", adm_name
                yield num, "adm_path_2", adm_paths[adm_name][0] if adm_name in adm_paths else ""
                yield num, "adm_path_3", adm_paths[adm_name][1] if adm_name in adm_paths else ""
