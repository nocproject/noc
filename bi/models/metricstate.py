# ----------------------------------------------------------------------
# Metrics Log
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    Int16Field,
    StringField,
)
from noc.core.clickhouse.engines import ReplacingMergeTree
from noc.core.translation import ugettext as _


class MetricState(Model):
    class Meta(object):
        db_table = "metricstate"
        engine = ReplacingMergeTree("date", ("node_id",))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Log Updated"))
    node_id = StringField(description=_("Node Id"))
    node_type = StringField(description=_("Node Type"), low_cardinality=True)
    slot = Int16Field(description=_("Slot number"))
    state = StringField(description=_("Node state"))
