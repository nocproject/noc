# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MAC Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField, DateTimeField, UInt64Field, UInt16Field, UInt8Field,
    StringField, ReferenceField)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.interfaceprofile import InterfaceProfile
from noc.core.bi.dictionaries.networksegment import NetworkSegment
from noc.core.translation import ugettext as _


class MAC(Model):
    """
    MAC address table snapshot
    
    Common queries:
    
    Last seen MAC location:
    
    SELECT timestamp, object, interface 
    FROM mac 
    WHERE 
      date >= ? 
      AND mac = ?
       AND uni = 1 
    ORDER BY timestamp DESC LIMIT 1;
    
    All MAC locations for date interval:

    SELECT timestamp, object, interface 
    FROM mac 
    WHERE 
      date >= ? 
      AND mac = ? 
      AND uni = 1;
    """
    class Meta:
        db_table = "mac"
        engine = MergeTree("date", ("ts", "managed_object"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObject,
        description=_("Object Name")
    )
    mac = UInt64Field(description=_("MAC"))
    interface = StringField(description=_("Interface"))
    interface_profile = ReferenceField(
        InterfaceProfile,
        description=_("Interface Profile")
    )
    segment = ReferenceField(
        NetworkSegment,
        description=_("Network Segment")
    )
    vlan = UInt16Field(description=_("VLAN"))
    is_uni = UInt8Field(description=_("Is UNI"))
