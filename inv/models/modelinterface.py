## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelInterface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, ListField,
                                EmbeddedDocumentField)
## NOC modules
from noc.lib.escape import json_escape as q


A_TYPE = ["str", "int", "float", "bool", "objectid", "ref"]


class ModelInterfaceAttr(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = StringField()
    type = StringField(choices=[(t, t) for t in A_TYPE])
    description = StringField()
    required = BooleanField(default=False)
    is_const = BooleanField(default=False)
    # default
    # ref

    def __unicode__(self):
        return self.name

    def __eq__(self, v):
        return (
            self.name == v.name and
            self.type == v.type and
            self.description == v.description and
            self.required == v.required and
            self.is_const == v.is_const
        )


class ModelInterface(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.modelinterfaces",
        "allow_inheritance": False,
    }

    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField()
    attrs = ListField(EmbeddedDocumentField(ModelInterfaceAttr))

    def __unicode__(self):
        return self.name

    def to_json(self):
        ar = []
        for a in self.attrs:
            r = ["            {"]
            r += ["                \"name\": \"%s\"," % q(a.name)]
            r += ["                \"type\": \"%s\"," % q(a.type)]
            r += ["                \"description\": \"%s\"," % q(a.description)]
            r += ["                \"required\": %s," % q(a.required)]
            r += ["                \"is_const\": %s" % q(a.is_const)]
            r += ["            }"]
            ar += ["\n".join(r)]

        r = [
            "[",
            "    {",
            "        \"name\": \"%s\"," % q(self.name),
            "        \"description\": \"%s\"," % q(self.description),
            "        \"attrs\": [",
            ",\n".join(ar),
            "        ]",
            "    }",
            "]"
        ]
        return "\n".join(r)
