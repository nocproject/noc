# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dashboard Layout
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField, IntField,
                                ListField, EmbeddedDocumentField)
from noc.lib.prettyjson import to_json


class DashboardCell(EmbeddedDocument):
    name = StringField()
    # Row number
    row = IntField(min_value=0)
    # Height
    height = IntField()
    # Extra small devices columns (Phones, <768px)
    xs = IntField()
    # Small devices columns (Tablets, <992px)
    sm = IntField()
    # Medium devices (Desktop, <1200px)
    md = IntField()
    # Large devices (Desktop, > 1200px)
    lg = IntField()

    def __unicode__(self):
        return self.name

    def to_json(self, *args, **kwargs):
        return {
            "name": self.name,
            "row": self.row,
            "xs": self.xs,
            "sm": self.sm,
            "md": self.md,
            "lg": self.lg,
            "height": self.height
        }


class DashboardLayout(Document):
    meta = {
        "collection": "noc.dashboardlayouts",
        "json_collection": "bi.dashboardlayouts"
    }

    name = StringField()
    uuid = UUIDField(binary=True)
    description = StringField()
    # @todo: Add preview
    cells = ListField(EmbeddedDocumentField(DashboardCell))

    def __unicode__(self):
        return self.name

    def to_json(self):
        return to_json({
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "cells": [s.to_json() for s in self.cells]
        }, order=["name", "uuid", "description", "cells"])

    def get_json_path(self):
        return "%s.json" % self.name
