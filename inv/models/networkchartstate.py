## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Chart State
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, StringField, DictField,
                           IntField)


class NetworkChartState(Document):
    """
    Network Chart State
    """
    meta = {
        "collection": "noc.inv.networkchartstate",
        "allow_inheritance": False,
        "indexes": [("chart", "type", "object")]
    }

    chart = IntField()   # Network chart reference
    type = StringField(
        choices=[
            ("mo", "Managed Object"),
            ("link", "Link")
        ])
    object = StringField()  # Object reference
    state = DictField()  # Arbitrary state data

    def __unicode__(self):
        return "%s %s %s" % (self.chart, self.type, self.object)
