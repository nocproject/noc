# ----------------------------------------------------------------------
# NetworkSegment dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.core.clickhouse.fields import StringField, ReferenceField


class NetworkSegment(Dictionary):
    class Meta(object):
        name = "networksegment"
        layout = "hashed"

    name = StringField()
    parent = ReferenceField("self")
