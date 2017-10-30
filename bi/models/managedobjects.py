# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (DateField, DateTimeField,
                                        UInt16Field,
                                        Int32Field, BooleanField,
                                        StringField,
                                        Float64Field, ReferenceField,
                                        IPv4Field, UInt8Field)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject as ManagedObjectDict
from noc.core.bi.dictionaries.pool import Pool
from noc.core.bi.dictionaries.profile import Profile
from noc.core.bi.dictionaries.vendor import Vendor
from noc.core.bi.dictionaries.platform import Platform
from noc.core.bi.dictionaries.version import Version
from noc.core.bi.dictionaries.administrativedomain import AdministrativeDomain
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.bi.dictionaries.container import Container
from noc.core.translation import ugettext as _
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainM


class ManagedObject(Model):
    class Meta:
        db_table = "managedobjects"
        engine = MergeTree("date", ("managed_object", "ts"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObjectDict,
        description=_("Object Name")
    )
    # Location
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))
    segment = ReferenceField(NetworkSegment, description=_("Network Segment"))
    container = ReferenceField(Container, description=_("Container"))
    level = UInt16Field(description=_("Level"))
    # Coordinates
    x = Float64Field(description=_("Longitude"))
    y = Float64Field(description=_("Latitude"))
    # Management
    pool = ReferenceField(Pool, description=_("Pool Name"))
    name = StringField(description=_("Name"))
    address = IPv4Field(description=_("Address"))
    is_managed = BooleanField(description=_("Is Managed"))
    # Platform
    profile = ReferenceField(Profile, description=_("Profile"))
    vendor = ReferenceField(Vendor, description=_("Vendor"))
    platform = ReferenceField(Platform, description=_("Platform"))
    version = ReferenceField(Version, description=_("Version"))
    n_interfaces = Int32Field(description=_("Interface count"))
    n_subscribers = Int32Field(description=_("Interface count"))
    n_services = Int32Field(description=_("Interface count"))
    # Topology
    n_neighbors = Int32Field(description=_("Neighbors"))
    n_links = Int32Field(description=_("Interface count"))
    nri_links = Int32Field(description=_("Links (NRI)"))
    mac_links = Int32Field(description=_("Links (MAC)"))
    stp_links = Int32Field(description=_("Links (STP)"))
    lldp_links = Int32Field(description=_("Links (LLDP)"))
    cdp_links = Int32Field(description=_("Links (CDP)"))
    # Capabilities
    has_stp = BooleanField(description=_("Has STP"))
    has_lldp = BooleanField(description=_("Has LLDP"))
    has_cdp = BooleanField(description=_("Has CDP"))
    has_snmp = BooleanField(description=_("Has SNMP"))
    has_snmp_v1 = BooleanField(description=_("Has SNMP v1"))
    has_snmp_v2c = BooleanField(description=_("Has SNMP v2c"))

    @classmethod
    def transform_query(cls, query, user):
        if not user or user.is_superuser:
            return query  # No restrictions
        # Get user domains
        domains = UserAccess.get_domains(user)
        # Resolve domains against dict
        domain_ids = [
            x.bi_id
            for x in AdministrativeDomainM.objects.filter(id__in=domains)
        ]
        filter = query.get("filter", {})
        dl = len(domain_ids)
        if not dl:
            return None
        elif dl == 1:
            q = {
                "$eq": [
                    {"$field": "administrative_domain"},
                    domain_ids[0]
                ]
            }
        else:
            q = {
                "$in": [
                    {"$field": "administrative_domain"},
                    domain_ids
                ]
            }
        if filter:
            query["filter"] = {
                "$and": [query["filter"], q]
            }
        else:
            query["filter"] = q
        return query
