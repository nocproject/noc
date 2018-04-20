# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# ActionCommands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
# Third-party modules
=======
##----------------------------------------------------------------------
## ActionCommands
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField,
                                BooleanField, ListField, IntField,
                                EmbeddedDocumentField, ReferenceField)
<<<<<<< HEAD
# NOC modules
from noc.lib.nosql import PlainReferenceField
from .profile import Profile
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from .action import Action
=======
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from action import Action
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


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
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.actioncommands",
        "json_depends_on": [
            "sa.actions",
            "sa.profile"
=======
        "json_collection": "sa.actioncommands",
        "json_depends_on": [
            "sa.actions"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ]
    }
    name = StringField(unique=True)
    uuid = UUIDField(unique=True)
    action = ReferenceField(Action)
    description = StringField()
<<<<<<< HEAD
    profile = PlainReferenceField(Profile)
=======
    profile = StringField()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    config_mode = BooleanField(default=False)
    match = ListField(EmbeddedDocumentField(PlatformMatch))
    commands = StringField()
    preference = IntField(default=1000)
    timeout = IntField(default=60)

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "action__name": self.action.name,
            "description": self.description,
<<<<<<< HEAD
            "profile__name": self.profile.name,
=======
            "profile": self.profile,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            "config_mode": self.config_mode,
            "match": [c.json_data for c in self.match],
            "commands": self.commands,
            "preference": self.preference,
            "timeout": self.timeout
        }
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "$collection", "uuid",
                              "action__name",
                              "description",
<<<<<<< HEAD
                              "profile__name",
=======
                              "profile",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                              "config_mode",
                              "preference",
                              "match",
                              "commands",
                              "timeout"
                              ])
