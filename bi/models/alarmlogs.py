# ----------------------------------------------------------------------
# Alarm Logs Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    StringField,
    ReferenceField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.alarmclass import AlarmClass
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class AlarmLogs(Model):
    class Meta(object):
        db_table = "alarmlogs"
        engine = MergeTree("date", ("ts", "alarm_id"), primary_keys=("ts", "alarm_id"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Log Created"))
    alarm_id = StringField(description=_("Id"))
    alarm_ts = DateTimeField(description=_("Alarm Clear Time"))
    alarm_clear_ts = DateTimeField(description=_("Alarm Close Time"))
    alarm_class = ReferenceField(AlarmClass, description=_("Alarm Class"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    ack_user = StringField(description=_("Manual acknowledgement user name"))
    ack_ts = DateTimeField(description=_("Manual acknowledgement timestamp"))
    alarm_escalation_ts = DateTimeField(description=_("Escalation Time"))
    alarm_escalation_tt = StringField(description=_("Number of Escalation"))
    from_status = StringField(description=_("Message Source"), low_cardinality=True)
    to_status = StringField(description=_("Message Source"), low_cardinality=True)
    source = StringField(description=_("Message Source"), low_cardinality=True)
    message = StringField(description=_("Log Message"))
