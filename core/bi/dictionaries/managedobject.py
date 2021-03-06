# ----------------------------------------------------------------------
# ManagedObject dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField


class ManagedObject(Dictionary):
    class Meta(object):
        name = "managedobject"
        layout = "hashed"

    name = StringField()
    address = StringField()
    profile = StringField()
    platform = StringField()
    version = StringField()
    remote_id = StringField()
    remote_system = StringField()
    administrative_domain_id = StringField()
    administrative_domain = StringField()
    location_address = StringField()
