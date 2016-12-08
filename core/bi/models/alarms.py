# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarms Model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (DateField, DateTimeField,
                                        Int32Field, Int64Field,
                                        StringField,
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
from noc.core.bi.dictionaries.alarmclass import AlarmClass


class Alarms(Model):
    class Meta:
        db_table = "alarms"
        engine = MergeTree("date", ("ts", "managed_object"))

    date = DateField()
    ts = DateTimeField()
    close_ts = DateTimeField()
    alarm_id = StringField()
    root = StringField()
    alarm_class = ReferenceField(AlarmClass)
    severity = Int32Field()
    reopens = Int32Field()
    direct_services = Int64Field()
    direct_subscribers = Int64Field()
    total_objects = Int64Field()
    total_services = Int64Field()
    total_subscribers = Int64Field()
    managed_object = ReferenceField(ManagedObject)
    ip = IPv4Field()
    profile = ReferenceField(Profile)
    vendor = ReferenceField(Vendor)
    platform = ReferenceField(Platform)
    version = ReferenceField(Version)
    administrative_domain = ReferenceField(AdministrativeDomain)
    segment = ReferenceField(NetworkSegment)
    container = ReferenceField(Container)
    # Coordinates
    x = Float64Field()
    y = Float64Field()
