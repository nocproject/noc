# ----------------------------------------------------------------------
# Purgatorium
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    BooleanField,
    StringField,
    IPv4Field,
    ReferenceField,
    MapField,
    ArrayField,
    MaterializedField,
    UInt64Field,
)
from noc.core.clickhouse.engines import ReplacingMergeTree
from noc.core.bi.dictionaries.pool import Pool
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class Purgatorium(Model):
    class Meta(object):
        db_table = "purgatorium"
        engine = ReplacingMergeTree(
            "date",
            ("pool", "ip", "source", "remote_system"),
        )

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Registered Record"))
    # Require fields
    ip = IPv4Field(description="IP Address")
    pool = ReferenceField(Pool, description=_("Pool Name"))
    source = StringField(low_cardinality=True)
    # network-scan
    # neighbors
    # syslog-source
    # trap-source
    # manual
    # etl
    # Network-Scan, Neighbor fields
    description = StringField(description="Description")
    chassis_id = StringField(description="Chassis ID")
    hostname = StringField(description="Hostname Discovery")
    uptime = UInt64Field(description="Host Uptime")
    border = ReferenceField(ManagedObject, description=_("Object Name"))
    # Set for records on RemoteSystem
    data = MapField(StringField(), description=_("Vars"))
    # Json Field  {check: str PING, avail: True/False, access: None, error: None, port}
    checks = ArrayField(StringField())
    #
    success_checks = MaterializedField(
        ArrayField(StringField(low_cardinality=True)),
        """arrayMap(
             x -> trim(TRAILING ':' from concat(JSONExtractString(x, 'check'), ':', JSONExtractString(x, 'port'))),
             arrayFilter(c -> JSONExtractBool(c, 'status') ,checks)
         )""",
        low_cardinality=False,
    )
    # http, telegraf HTTP and port 3000, regex - status: avail & access & app (regex)
    is_delete = BooleanField(description="Address was removed from RemoteSystem", default=False)
    # Labels List
    labels = ArrayField(StringField(), description=_("Tags"))
    service_groups = ArrayField(UInt64Field(), description=_("Service Groups Ids"))
    clients_groups = ArrayField(UInt64Field(), description=_("Client Groups Ids"))
    remote_system = StringField(description="Remote System")
    remote_id = StringField(description="Remote System Id")
    # Maybe fields for detect hints
    # available_ports - detect open TCP port
    # maybe_agent
    # maybe_managed_object - bool
