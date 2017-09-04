# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# routing_neighbors table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField, DateTimeField, UInt64Field, StringField, ReferenceField)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject


class RoutingNeighbors(Model):
    class Meta:
        db_table = "mac"
        engine = MergeTree("date", ("managed_object", "ts"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObject,
        description=_("Object Name")
    )
    interface = StringField()
    subinterface = StringField()
    neighbor_address = StringField()
    neighbor_object = ReferenceField(
        ManagedObject,
        description=_("Object Name")
    )
    protocol = StringField()
    bgp_local_as = UInt64Field()
    bgp_remote_as = UInt64Field()
