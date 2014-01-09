## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ConnectionRule model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField,
                                ListField, EmbeddedDocumentField)
## NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path


class Context(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    type = StringField()
    scope = StringField()
    reset_scopes = ListField(StringField())

    def __unicode__(self):
        return u"%s, %s" % (self.type, self.scope)

    def __eq__(self, other):
        return (
            self.type == other.type and
            self.scope == other.scope and
            self.reset_scopes == other.reset_scopes
        )

    @property
    def json_data(self):
        r = {
            "type": self.type,
            "scope": self.scope,
            "reset_scopes": self.reset_scopes
        }
        return r


class Rule(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    match_type = StringField()
    match_connection = StringField()
    scope = StringField()
    target_type = StringField()
    target_number = StringField()
    target_connection = StringField()

    def __unicode__(self):
        return "%s:%s -(%s)-> %s %s:%s" % (
            self.match_type, self.match_connection, self.scope,
            self.target_type, self.target_number,
            self.target_connection)

    def __eq__(self, other):
        return (
            self.match_type == other.match_type and
            self.match_connection == other.match_connection and
            self.scope == other.scope and
            self.target_type == other.target_type and
            self.target_number == other.target_number and
            self.target_connection == other.target_connection
        )

    @property
    def json_data(self):
        return {
            "match_type": self.match_type,
            "match_connection": self.match_connection,
            "scope": self.scope,
            "target_type": self.target_type,
            "target_number": self.target_number,
            "target_connection": self.target_connection
        }


class ConnectionRule(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.connectionrules",
        "allow_inheritance": False,
        "indexes": []
    }

    name = StringField(unique=True)
    description = StringField()
    context = ListField(EmbeddedDocumentField(Context))
    rules = ListField(EmbeddedDocumentField(Rule))
    uuid = UUIDField(binary=True)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        return {
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description,
            "context": [c.json_data for c in self.context],
            "rules": [c.json_data for c in self.rules]
        }

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "uuid", "description"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
