# ----------------------------------------------------------------------
# DisposeLog Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    StringField,
    ReferenceField,
    UInt32Field,
    UInt64Field,
    MapField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.bi.dictionaries.eventclass import EventClass
from noc.core.bi.dictionaries.alarmclass import AlarmClass
from noc.core.translation import ugettext as _


class DisposeLog(Model):
    class Meta(object):
        db_table = "disposelog"
        engine = MergeTree(
            "date",
            ("date", "managed_object"),
            primary_keys=("date", "managed_object"),
            partition_function="toYYYYMMDD(ts)",
        )

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    event_id = StringField(description=_("Event ID"))
    alarm_id = StringField(description=_("Alarm ID"))
    op = StringField(description=_("Operation"), low_cardinality=True)  # raise, clear, drop, ignore
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    event_class = ReferenceField(EventClass, description=_("Event Class"))
    alarm_class = ReferenceField(AlarmClass, description=_("Alarm Class"))
    message = StringField(description=_("Event Message"))
    target = MapField(StringField(), description=_("Target"))
    target_reference = UInt64Field(description="Target reference")
    reopens = UInt32Field(description=_("Reopens"))
