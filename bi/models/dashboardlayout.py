# ----------------------------------------------------------------------
# Dashboard Layout
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, UUIDField, IntField, ListField, EmbeddedDocumentField

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path


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

    def __str__(self):
        return self.name

    def to_json(self, *args, **kwargs):
        return {
            "name": self.name,
            "row": self.row,
            "xs": self.xs,
            "sm": self.sm,
            "md": self.md,
            "lg": self.lg,
            "height": self.height,
        }


class DashboardLayout(Document):
    meta = {
        "collection": "noc.dashboardlayouts",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "bi.dashboardlayouts",
    }

    name = StringField()
    uuid = UUIDField(binary=True)
    description = StringField()
    # @todo: Add preview
    cells = ListField(EmbeddedDocumentField(DashboardCell))

    def __str__(self):
        return self.name

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "uuid": self.uuid,
                "description": self.description,
                "cells": [s.to_json() for s in self.cells],
            },
            order=["name", "uuid", "description", "cells"],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)
