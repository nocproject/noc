## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ModelInterface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, ListField,
                                EmbeddedDocumentField, UUIDField)
## NOC modules
from error import ModelDataError
from noc.lib.utils import deep_copy
from noc.lib.escape import json_escape as q
from noc.sa.interfaces.base import (StringParameter, BooleanParameter,
                                    FloatParameter, IntParameter)

T_MAP = {
    "str": StringParameter(),
    "int": IntParameter(),
    "float": FloatParameter(),
    "bool": BooleanParameter()
}

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

    def _clean(self, value):
        return getattr(self, "clean_%s" % self.type)(value)

    def clean_str(self, value):
        return value

    def clean_int(self, value):
        return int(value)

    def clean_float(self, value):
        if isinstance(value, basestring):
            return float(value.replace(",", "."))
        else:
            return float(value)

    def clean_bool(self, value):
        value = value.lower()
        if value in ("yes", "y", "t", "true"):
            return True
        try:
            v = int(value)
            return v != 0
        except ValueError:
            return False


class ModelInterface(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.modelinterfaces",
        "allow_inheritance": False,
        "json_collection": "inv.modelinterfaces"
    }

    name = StringField(unique=True)
    description = StringField()
    attrs = ListField(EmbeddedDocumentField(ModelInterfaceAttr))
    uuid = UUIDField(binary=True)

    def __unicode__(self):
        return self.name

    def get_attr(self, name):
        for a in self.attrs:
            if a.name == name:
                return a
        return None

    def to_json(self):
        ar = []
        for a in self.attrs:
            r = ["        {"]
            r += ["            \"name\": \"%s\"," % q(a.name)]
            r += ["            \"type\": \"%s\"," % q(a.type)]
            r += ["            \"description\": \"%s\"," % q(a.description)]
            r += ["            \"required\": %s," % q(a.required)]
            r += ["            \"is_const\": %s" % q(a.is_const)]
            r += ["        }"]
            ar += ["\n".join(r)]
        r = [
            "{",
            "    \"name\": \"%s\"," % q(self.name),
            "    \"uuid\": \"%s\"," % str(self.uuid),
            "    \"description\": \"%s\"," % q(self.description),
            "    \"attrs\": [",
            ",\n".join(ar),
            "    ]",
            "}",
        ]
        return "\n".join(r) + "\n"

    def get_json_path(self):
        p = [n.strip() for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def clean_data(cls, data):
        """
        Convert types accoding to interface
        """
        d = deep_copy(data)
        for i_name in d:
            mi = ModelInterface.objects.filter(name=i_name).first()
            if not mi:
                raise ModelDataError("Unknown interface '%s'" % i_name)
            v = d[i_name]
            for a in mi.attrs:
                if a.name in v:
                    v[a.name] = T_MAP[a.type]._clean(v[a.name])
        return d
