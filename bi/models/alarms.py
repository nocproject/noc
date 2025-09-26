# ----------------------------------------------------------------------
# Alarms Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model, NestedModel
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    Int16Field,
    Int32Field,
    Int64Field,
    StringField,
    Float64Field,
    ReferenceField,
    IPv4Field,
    NestedField,
    UInt32Field,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.vendor import Vendor
from noc.core.bi.dictionaries.platform import Platform
from noc.core.bi.dictionaries.version import Version
from noc.core.bi.dictionaries.profile import Profile
from noc.core.bi.dictionaries.objectprofile import ObjectProfile
from noc.core.bi.dictionaries.administrativedomain import AdministrativeDomain
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.bi.dictionaries.container import Container
from noc.core.bi.dictionaries.alarmclass import AlarmClass
from noc.core.bi.dictionaries.pool import Pool
from noc.core.bi.dictionaries.project import Project
from noc.core.translation import ugettext as _
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainM
from noc.config import config


class Services(NestedModel):
    profile = StringField(description="Profile Name")
    summary = UInt32Field(description="Summary")


class Subscribers(NestedModel):
    profile = StringField(description="Profile Name")
    summary = UInt32Field(description="Summary")


class Alarms(Model):
    class Meta(object):
        db_table = "alarms"
        engine = MergeTree(
            "date", ("ts", "managed_object", "alarm_class"), primary_keys=("ts", "managed_object")
        )

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    close_ts = DateTimeField(description=_("Close Time"))
    duration = Int32Field(description=_("Duration"))
    alarm_id = StringField(description=_("Id"))
    root = StringField(description=_("Alarm Root"))
    rca_type = Int16Field(description=_("RCA Type"))
    alarm_class = ReferenceField(AlarmClass, description=_("Alarm Class"))
    severity = Int32Field(description=_("Severity"))
    reopens = Int32Field(description=_("Reopens"))
    direct_services = Int64Field(description=_("Direct Services"))
    direct_subscribers = Int64Field(description=_("Direct Subscribers"))
    total_objects = Int64Field(description=_("Total Objects"))
    total_services = Int64Field(description=_("Total Services"))
    total_subscribers = Int64Field(description=_("Total Subscribers"))
    escalation_ts = DateTimeField(description=_("Escalation Time"))
    escalation_tt = StringField(description=_("Number of Escalation"))
    # Amount of reboots during alarm
    reboots = Int16Field(description=_("Qty of Reboots"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    pool = ReferenceField(Pool, description=_("Pool Name"))
    object_profile = ReferenceField(ObjectProfile, description=_("Object Profile"))
    ip = IPv4Field(description=_("IP Address"))
    profile = ReferenceField(Profile, description=_("Profile"))
    vendor = ReferenceField(Vendor, description=_("Vendor Name"))
    platform = ReferenceField(Platform, description=_("Platform"))
    version = ReferenceField(Version, description=_("Version"))
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))
    segment = ReferenceField(NetworkSegment, description=_("Network Segment"))
    container = ReferenceField(Container, description=_("Container"))
    project = ReferenceField(Project, description=_("Project"))
    # Coordinates
    x = Float64Field(description=_("Longitude"))
    y = Float64Field(description=_("Latitude"))
    services = NestedField(Services, description=_("Affected Services"))
    subscribers = NestedField(Subscribers, description=_("Affected Subscribers"))
    # location = StringField(description="Location")
    # Ack info
    ack_user = StringField(description=_("Manual acknowledgement user name"))
    ack_ts = DateTimeField(description=_("Manual acknowledgement timestamp"))

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
        if dl == 1:
            q = {"$eq": [{"$field": "administrative_domain"}, domain_ids[0]]}
        else:
            q = {"$in": [{"$field": "administrative_domain"}, domain_ids]}
        if filter:
            query["filter"] = {"$and": [query["filter"], q]}
        else:
            query["filter"] = q
        return query

    @classmethod
    def transform_field(cls, field):
        if field == "services":
            return ",".join(
                [
                    f"arrayStringConcat(arrayMap(x -> concat(dictGetString('{config.clickhouse.db_dictionaries}.serviceprofile'",
                    " 'name', toUInt64(services.profile[indexOf(services.summary, x)]))",
                    " ':', toString(x)), services.summary),',')",
                ]
            )

        if field == "subscribers":
            return ",".join(
                [
                    f"arrayStringConcat(arrayMap(x -> concat(dictGetString('{config.clickhouse.db_dictionaries}.subscriberprofile'",
                    " 'name', toUInt64(subscribers.profile[indexOf(subscribers.summary, x)]))",
                    " ':', toString(x)), subscribers.summary),',')",
                ]
            )
        return field
