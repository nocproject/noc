# ----------------------------------------------------------------------
# Check History model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    ReferenceField,
    StringField,
    UInt16Field,
    UInt32Field,
    BooleanField,
    IPv4Field,
    MapField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.service import Service
from noc.core.bi.dictionaries.remotesystem import RemoteSystem
from noc.core.translation import ugettext as _


class CheckHistory(Model):
    class Meta:
        db_table = "checkhistory"
        engine = MergeTree("date", ("date", "check_name"), primary_keys=("date", "check_name"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    check_name = StringField(description=_("Check Name"), low_cardinality=True)
    status = BooleanField(description=_("Check Result status"))
    key = StringField(description=_("Check Key"))
    ttl = UInt32Field(description=_("Check actual time (in seconds)"))
    args = MapField(StringField(), description="Running Argument")
    port = UInt16Field(description=_("TCP/UDP Port"))
    address = IPv4Field(description="Destination IP Address")
    source = StringField(description=_("Source"), low_cardinality=True)
    script = StringField(description=_("Diagnostic Name"), low_cardinality=True)
    skipped = BooleanField()
    # Error
    error = StringField(description="Error text")
    error_code = StringField(description="Error code")
    is_available = BooleanField()
    is_access = BooleanField()
    data = StringField(description=_("Collected data (JSON)"))
    managed_object = ReferenceField(ManagedObject, description=_("Running for object"))
    service = ReferenceField(Service, description=_("Object Name"))
    # agent = ReferenceField(Agent, description=_("Object Name"))
    remote_system = ReferenceField(RemoteSystem, description=_("Remote System"))

    @classmethod
    def transform_query(cls, query, user):
        return query
