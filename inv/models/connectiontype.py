## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ConnectionType model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, DictField,
                                ListField)
## NOC modules
from noc.lib.nosql import PlainReferenceField
from noc.lib.prettyjson import to_json


class ConnectionType(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.connectiontypes",
        "allow_inheritance": False,
        "indexes": ["extend", "data", "c_group"]
    }

    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField()
    # Type extends another type, if not null
    extend = PlainReferenceField("self", required=False)
    # List of available genders
    genders = StringField(
        choices=[
            "s",  # Genderless connection
            "ss",  # Genderless connection 2 or more objects
            "m",  # Only male type
            "f",  # Only female type
            "mmf",  # female, 1 or more males
            "mf",  # male-female
            "mff"  # male, 2 or more females
        ], default="mf")
    # ModelData
    data = DictField(default={})
    # Compatible group
    # Connection compatible with opposite gender of same type
    # and all types having any c_group
    c_group = ListField(StringField())

    OPPOSITE_GENDER = {
        "s": "s",
        "m": "f",
        "f": "m"
    }

    def __unicode__(self):
        return self.name

    def to_json(self):
        r = {
            "name": self.name,
            "description": self.description,
            "genders": self.genders,
            "c_group": self.c_group
        }
        if self.extend:
            r["extend__name"] = self.extend.name
        return to_json([r], order=["name", "description"])

    def get_effective_data(self):
        """
        Calculate effective data
        :return:
        """
        raise NotImplementedError

    def get_superclasses(self):
        s = []
        c = self
        while c:
            c = c.extend
            if c:
                s += [c]
        return s

    def get_subclasses(self):
        s = []
        for c in ConnectionType.objects.filter(extend=self.id):
            s += [c] + c.get_subclasses()
        return s

    def get_inheritance_path(self, other):
        s = []
        # Upward direction
        c = self
        while c:
            s.insert(0, c)
            if other.id == c.id:
                return s
            c = c.extend
        # Not found, try downward direction
        s = []
        c = other
        while c:
            s.insert(0, c)
            if self.id == c.id:
                return s
            c = c.extend
        return s

    def get_by_c_group(self):
        c_group = self.c_group
        if not c_group:
            return []
        r = []
        for ct in ConnectionType.objects.filter(c_group__in=c_group):
            if ct.id != self.id:
                r += [ct]
        return r

    def get_compatible_types(self, gender):
        r = []
        og = self.OPPOSITE_GENDER[gender]
        # Add self type if opposige gender allowed
        if og in self.genders:
            r += [self.id]
        if gender in ["m", "s"]:
            # Add superclasses
            for c in self.get_superclasses():
                if og in c.genders:
                    r += [c.id]
        if gender in ["f", "s"]:
            # Add subclasses
            for c in self.get_subclasses():
                if og in c.genders:
                    r += [c.id]
        if self.c_group:
            for c in self.get_by_c_group():
                if og in c.genders:
                    r += [c.id]
        return r
