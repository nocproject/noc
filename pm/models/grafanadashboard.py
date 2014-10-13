## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Metric model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField


class GrafanaDashboard(Document):
    meta = {
        "collection": "noc.pm.grafanadashboard"
    }

    name = StringField(unique=True)
    title = StringField()
    tags = ListField(StringField())
    dashboard = StringField()

    def __unicode__(self):
        return self.title
