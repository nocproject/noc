# ----------------------------------------------------------------------
# Diagnostic History model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    UInt8Field,
    ReferenceField,
    StringField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject

# from noc.core.bi.dictionaries.service import Service
from noc.core.translation import ugettext as _


class DiagnosticHistory(Model):
    class Meta(object):
        db_table = "diagnostichistory"
        engine = MergeTree("date", ("date", "diagnostic"), primary_keys=("date", "diagnostic"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    # diagnostic = ReferenceField(ManagedObject, description=_("Object Name"))
    diagnostic_name = StringField(description=_("Diagnostic Name"))
    # agent = ReferenceField(Agent, description=_("Object Name"))
    # service = ReferenceField(ManagedObject, description=_("Object Name"))
    from_state = StringField(description=_("From state"))
    state = StringField(description=_("Current diagnotic state"))
    data = StringField(description=_("Collected data (JSON)"))

    @classmethod
    def transform_query(cls, query, user):
        return query
