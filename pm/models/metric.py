## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, StringField, BinaryField)


class Metric(Document):
    meta = {
        "collection": "noc.ts.metrics",
        "indexes": ["parent"]
    }

    name = StringField(unique=True)
    hash = BinaryField(unique=True)
    parent = StringField()

    def __unicode__(self):
        return self.metric
