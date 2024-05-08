# ----------------------------------------------------------------------
# Alarms Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    StringField,
    ReferenceField,
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
    event_id = StringField(description=_("Id"))
    event_class = ReferenceField(EventClass, description=_("Event Class"))
    source = StringField(description=_("Id"), low_cardinality=True)
    # Tags
    labels = ArrayField(StringField(), description=_("Tags"))
    data = StringField(description="All data on JSON")
    raw_vars = MapField(StringField(), description=_("Raw Variables"))
    resolved_vars = MapField(StringField(), description=_("Resolved Variables"))
    vars = MapField(StringField(), description=_("Vars"))
    #
    remote_system = ReferenceField(RemoteSystem, description="Remote System")
    remote_id = StringField(description="Event Id on Remote System")
    #
    snmp_trap_oid = StringField(description=_("snmp Trap OID"))
    message = StringField(description=_("Syslog Message"))
    target = MapField(StringField(), description=_("Vars"))
    # Object
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    pool = ReferenceField(Pool, description=_("Pool Name"))
    ip = IPv4Field(description=_("IP Address"))
    profile = ReferenceField(Profile, description=_("Profile"))
    vendor = ReferenceField(Vendor, description=_("Vendor Name"))
    platform = ReferenceField(Platform, description=_("Platform"))
    version = ReferenceField(Version, description=_("Version"))
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))

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
