# ----------------------------------------------------------------------
# ServiceOutages model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    UInt8Field,
    UInt64Field,
    StringField,
    BooleanField,
    ReferenceField,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.administrativedomain import AdministrativeDomain
from noc.core.translation import ugettext as _


class ServiceOutages(Model):
    class Meta(object):
        db_table = "serviceoutages"
        engine = MergeTree("date", ("date", "service"))

    date = DateField(description="Date")
    ts = DateTimeField(description="Created")
    # Service ID
    service = UInt64Field(description="Service BI ID")
    service_id = StringField(description="Service Object ID")

    # Outage
    start = DateTimeField(description=_("Start Outage"))
    stop = DateTimeField(description=_("End Outage"))

    from_status = UInt8Field(description="Oper Status on start interval")
    to_status = UInt8Field(description="Oper Status on end interval")
    in_maintenance = UInt8Field(description="Service In Maintenance State")

    final_register = BooleanField(
        description=_("End Outage Register (Service admin state to non-production)")
    )
    administrative_domain = ReferenceField(AdministrativeDomain, description=_("Admin. Domain"))
