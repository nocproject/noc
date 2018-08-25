# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Reboots model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (DateField, DateTimeField,
                                        Float64Field, ReferenceField,
                                        IPv4Field)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.vendor import Vendor
from noc.core.bi.dictionaries.platform import Platform
from noc.core.bi.dictionaries.version import Version
from noc.core.bi.dictionaries.profile import Profile
from noc.core.bi.dictionaries.administrativedomain import AdministrativeDomain
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.bi.dictionaries.container import Container
from noc.core.bi.dictionaries.pool import Pool
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainM
from noc.core.translation import ugettext as _


class Reboots(Model):
    class Meta:
        db_table = "reboots"
        engine = MergeTree("date", ("ts", "managed_object"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    pool = ReferenceField(Pool, description=_("Pool Name"))
    ip = IPv4Field(description=_("IP Address"))
    profile = ReferenceField(Profile, description=_("Profile"))
    vendor = ReferenceField(Vendor, description=_("Vendor Name"))
    platform = ReferenceField(Platform, description=_("Platform"))
    version = ReferenceField(Version, description=_("Version"))
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))
    segment = ReferenceField(NetworkSegment, description=_("Network Segment"))
    container = ReferenceField(Container, description=_("Container"))
    # Coordinates
    x = Float64Field(description=_("Longitude"))
    y = Float64Field(description=_("Latitude"))

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
