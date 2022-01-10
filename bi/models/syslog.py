# ----------------------------------------------------------------------
# Syslog model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    UInt8Field,
    ReferenceField,
    StringField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class Syslog(Model):
    class Meta(object):
        db_table = "syslog"
        engine = MergeTree("date", ("managed_object", "ts"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    facility = UInt8Field(description=_("Facility"))
    severity = UInt8Field(description=_("Severity"))
    message = StringField(description=_("Syslog Message"))

    @classmethod
    def transform_query(cls, query, user):
        return query
