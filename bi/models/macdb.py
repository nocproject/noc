# ----------------------------------------------------------------------
# MACDB Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import ViewModel
from noc.core.clickhouse.functions import ArgMax
from noc.core.clickhouse.fields import (
    UInt64Field,
    UInt16Field,
    StringField,
    ReferenceField,
    AggregatedField,
    DateTimeField,
)
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.interfaceprofile import InterfaceProfile
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.clickhouse.engines import AggregatingMergeTree
from noc.core.translation import ugettext as _


class MACDB(ViewModel):
    class Meta(object):
        db_table = "macdb"
        view_table_source = "raw_mac"
        engine = AggregatingMergeTree(
            None,
            ("mac", "managed_object",),
            primary_keys=("mac", "managed_object"),
        )

    last_seen = AggregatedField(
        "ts",
        DateTimeField(),
        ArgMax(),
        description="Last Seen mac",
    )
    mac = UInt64Field(description=_("MAC"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    interface = AggregatedField(
        "interface",
        StringField(),
        ArgMax(),
        description="Interface",
    )
    interface_profile = AggregatedField(
        "interface_profile",
        ReferenceField(InterfaceProfile),
        ArgMax(),
        description=_("Interface Profile"),
    )
    segment = AggregatedField(
        "segment",
        ReferenceField(NetworkSegment),
        ArgMax(),
        description=_("Network Segment"),
    )
    vlan = AggregatedField(
        "vlan",
        UInt16Field(),
        ArgMax(),
        description="Vlan Number",
    )
