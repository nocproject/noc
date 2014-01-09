# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SyntaxAlias model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, DictField)
## NOC modules
from noc.lib.prettyjson import to_json


class SyntaxAlias(Document):
    meta = {
        "collection": "noc.syntaxaliases",
        "allow_inheritance": False
    }
    name = StringField(unique=True, required=True)
    syntax = DictField(required=False)
    uuid = UUIDField(binary=True)
    # Lookup cache
    cache = None

    def __unicode__(self):
        return self.name

    @classmethod
    def rewrite(cls, name, syntax):
        if cls.cache is None:
            cls.cache = dict((o.name, o.syntax)
                             for o in cls.objects.all())
        return cls.cache.get(name, syntax)

    def get_json_path(self):
        return "%s.json" % self.name.replace(":", "_")

    def to_json(self):
        return to_json({
            "name": self.name,
            "uuid": self.uuid,
            "syntax": self.syntax
        }, order=["name", "uuid", "syntax"])
