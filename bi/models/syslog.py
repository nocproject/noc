# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Syslog model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import DateField, DateTimeField, UInt8Field, ReferenceField, StringField
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainM
from noc.core.translation import ugettext as _


class Syslog(Model):
    class Meta:
        db_table = "syslog"
        engine = MergeTree("date", ("managed_object", "ts"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    facility = UInt8Field(description=_("Facility"))
    severity = UInt8Field(description=_("Severity"))
    message = StringField()

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
