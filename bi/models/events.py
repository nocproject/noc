# ----------------------------------------------------------------------
# Events Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    StringField,
    ReferenceField,
    UInt64Field,
    UInt8Field,
    IPv4Field,
    MapField,
    ArrayField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.clickhouse.connect import ClickhouseClient
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.remotesystem import RemoteSystem
from noc.core.bi.dictionaries.vendor import Vendor
from noc.core.bi.dictionaries.platform import Platform
from noc.core.bi.dictionaries.version import Version
from noc.core.bi.dictionaries.profile import Profile
from noc.core.bi.dictionaries.administrativedomain import AdministrativeDomain
from noc.core.bi.dictionaries.eventclass import EventClass
from noc.core.bi.dictionaries.pool import Pool
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.bi.dictionaries.container import Container
from noc.core.translation import ugettext as _
from noc.config import config
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainM


class Events(Model):
    class Meta(object):
        db_table = "events"
        engine = MergeTree(
            "date",
            ("date", "managed_object", "event_class"),
            primary_keys=("date", "managed_object"),
            partition_function="toYYYYMMDD(ts)",
        )

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Register"))
    start_ts = DateTimeField(description=_("Created"))
    # Event Classification
    event_id = StringField(description=_("Id"))  #
    source = StringField(description=_("Event Source"), low_cardinality=True)
    event_class = ReferenceField(EventClass, description=_("Event Class"))
    # Data
    labels = ArrayField(StringField(), description=_("Labels"))
    data = StringField(description="All data on JSON")
    message = StringField(description=_("Syslog Message"))
    # Calculated data
    raw_vars = MapField(StringField(), description=_("Raw Variables"))  # For old query
    resolved_vars = MapField(StringField(), description=_("Resolved Variables"))
    vars = MapField(StringField(), description=_("Vars"))
    snmp_trap_oid = StringField(description=_("snmp Trap OID"))
    #
    severity = UInt8Field(description="EventSeverity")
    result_action = StringField(description="Result action for event")
    error_message = StringField(description="Error message")
    #
    remote_system = ReferenceField(RemoteSystem, description="Remote System")
    remote_id = StringField(description="Event Id on Remote System")
    # Target data
    target = MapField(StringField(), description=_("Target"))
    target_name = StringField(description=_("Target Name"))
    target_reference = UInt64Field(description=_("Target Reference"))
    pool = ReferenceField(Pool, description=_("Pool Name"))
    ip = IPv4Field(description=_("IP Address"))
    # Resolver target
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    # Agent
    profile = ReferenceField(Profile, description=_("Profile"))
    vendor = ReferenceField(Vendor, description=_("Vendor Name"))
    platform = ReferenceField(Platform, description=_("Platform"))
    version = ReferenceField(Version, description=_("Version"))
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))
    segment = ReferenceField(NetworkSegment, description=_("Network Segment"))
    container = ReferenceField(Container, description=_("Container"))

    @classmethod
    def transform_query(cls, query, user):
        if not user or user.is_superuser:
            return query  # No restrictions
        # Get user domains
        domains = UserAccess.get_domains(user)
        # Resolve domains against dict
        domain_ids = [x.bi_id for x in AdministrativeDomainM.objects.filter(id__in=domains)]
        filter = query.get("filter", {})
        dl = len(domain_ids)
        if not dl:
            return None
        elif dl == 1:
            q = {"$eq": [{"$field": "administrative_domain"}, domain_ids[0]]}
        else:
            q = {"$in": [{"$field": "administrative_domain"}, domain_ids]}
        if filter:
            query["filter"] = {"$and": [query["filter"], q]}
        else:
            query["filter"] = q
        return query

    @classmethod
    def check_old_schema(cls, connect: "ClickhouseClient", table_name: str) -> bool:
        """
        Check syntax
        :param connect:
        :param table_name:
        :return:
        """
        c1 = super().check_old_schema(connect=connect, table_name=table_name)
        # Check repeat_hash column
        c2 = connect.execute(
            f"""
        SELECT database
        FROM system.columns
        WHERE database = '{config.clickhouse.db}' AND table = 'events' AND name = 'repeat_hash'
        """
        )
        return not c2 and c1
