# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActionCommands
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField,
                                BooleanField, ListField,
                                EmbeddedDocumentField, ReferenceField)
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from action import Action


class PlatformMatch(EmbeddedDocument):
    platform_re = StringField()
    version_re = StringField()

    def __unicode__(self):
        return u"%s - %s" % (self.platform_re, self.version_re)

    @property
    def json_data(self):
        return {
            "platform_re": self.platform_re,
            "version_re": self.version_re
        }


class ActionCommands(Document):
    meta = {
        "collection": "noc.actioncommands",
        "json_collection": "sa.actioncommands"
    }
    name = StringField(unique=True)
    uuid = UUIDField(unique=True)
    action = ReferenceField(Action)
    description = StringField()
    profile = StringField()
    config_mode = BooleanField(default=False)
    match = ListField(EmbeddedDocumentField(PlatformMatch))
    commands = StringField()

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "action__name": self.action.name,
            "description": self.description,
            "profile": self.profile,
            "config_mode": self.config_mode,
            "match": [c.json_data for c in self.match],
            "commands": self.commands
        }
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "uuid",
                              "action__name",
                              "description",
                              "profile",
                              "config_mode",
                              "match",
                              "commands"
                              ])
