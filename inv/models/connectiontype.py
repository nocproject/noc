# ---------------------------------------------------------------------
# ConnectionType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Any, Dict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    DictField,
    ListField,
    UUIDField,
    ObjectIdField,
    EmbeddedDocumentField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.main.models.doccategory import category
from noc.core.model.decorator import on_delete_check


class ConnectionMatcher(EmbeddedDocument):
    # Matched scope
    scope = StringField()
    # Matching protocol
    protocol = StringField()

    def __str__(self):
        return "<ConnectionMatcher %s:%s>" % (self.scope, self.protocol)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "scope": self.scope,
            "protocol": self.protocol,
        }


@category
@on_delete_check(check=[("inv.ConnectionType", "extend")])
class ConnectionType(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.connectiontypes",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["extend", "data", "c_group"],
        "json_collection": "inv.connectiontypes",
        "json_unique_fields": ["name", "uuid"],
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
            "mff",  # male, 2 or more females
        ],
        default="mf",
    )
    # ModelData
    data = DictField(default={})
    # Compatible group
    # Connection compatible with opposite gender of same type
    # and all types having any c_group
    c_group = ListField(StringField())
    uuid = UUIDField(binary=True)
    # Connection matchers
    matchers = ListField(EmbeddedDocumentField(ConnectionMatcher))

    OPPOSITE_GENDER = {"s": "s", "m": "f", "f": "m"}
    category = ObjectIdField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "genders": self.genders,
            "c_group": self.c_group,
        }
        if self.extend:
            r["extend__name"] = self.extend.name
        if self.matchers:
            r["matchers"] = [m.json_data for m in self.matchers]
        return r

    def to_json(self) -> str:
        return to_json(self.json_data, order=["name", "$collection", "uuid", "description"])

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

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

    def get_matched_scopes(self, protocols):
        """
        Returns set of matched scopes against the list of protocols
        :param protocols:
        :return:
        """
        return set(m.scope for m in self.matchers if m.protocol in protocols)

    def is_matched_scope(self, scope, protocols):
        """
        Check if connection type matches scope against list of protocols
        :param scope:
        :param protocols:
        :return:
        """
        return any(True for m in self.matchers if m.scope == scope and m.protocol in protocols)
