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
            ("pool", "address", "source"),
            version_field=("pool", "address", "source"),
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
    border = ReferenceField(ManagedObject, description=_("Object Name"))
    # Set for records on RemoteSystem
    data = MapField(StringField(), description=_("Vars"))
    is_delete = BooleanField(description="Address was removed from RemoteSystem", default=False)
    remote_system = StringField(description="Remote System")
    remote_id = StringField(description="Remote System Id")
    # Maybe fields for detect hints
    # alailabels_ports - detect open TCP port
    # maybe_agent
    # maybe_managed_object - bool
