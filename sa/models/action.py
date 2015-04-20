# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Action
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField, IntField,
                                BooleanField, ListField,
                                EmbeddedDocumentField)
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
##

class ActionParameter(EmbeddedDocument):
    name = StringField()
    type = StringField(
        choices=[
            ("int", "int"),
            ("float", "float"),
            ("str", "str"),
            ("interface", "interface")
        ]
    )
    description = StringField()
    is_required = BooleanField(default=True)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "is_required": self.is_required
        }


class Action(Document):
    meta = {
        "collection": "noc.actions",
        "json_collection": "sa.actions"
    }
    uuid = UUIDField(unique=True)
    name = StringField(unique=True)
    label = StringField()
    description = StringField()
    access_level = IntField(default=15)
    # Optional handler for non-sa actions
    handler = StringField()
    #
    params = ListField(EmbeddedDocumentField(ActionParameter))

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "label": self.label,
            "description": self.description,
            "access_level": self.access_level
        }
        if self.handler:
            r["handler"] = self.handler
        r["params"] = [c.json_data for c in self.params]
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "uuid", "label",
                              "description",
                              "access_level",
                              "handler",
                              "params"])
