# ---------------------------------------------------------------------
# ConnectionRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import re
from typing import Any, Dict, Optional, List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    ListField,
    BooleanField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, PlainReferenceListField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.cm.models.configurationparam import ConfigurationParam, ParamSchema
from noc.cm.models.configurationscope import ConfigurationScope
from .protocol import Protocol
from .connectiontype import ConnectionType


class ConnectionRule(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    # Match section
    scope = PlainReferenceField(ConfigurationScope, required=True)
    match_context = StringField()
    match_connection_type: Optional[ConnectionType] = PlainReferenceField(ConnectionType)
    match_protocols: Optional[List["Protocol"]] = PlainReferenceListField(Protocol)
    # Param Section
    # param, is_hide, is_readonly, choices
    allowed_params: List["ConfigurationParam"] = PlainReferenceListField(ConfigurationParam)
    deny_params: List["ConfigurationParam"] = PlainReferenceListField(ConfigurationParam)
    disabled = BooleanField(default=False)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"scope__name": self.scope.name}
        if self.match_context:
            r["match_context"] = self.match_context
        if self.match_connection_type:
            r["match_connection_type__name"] = self.match_connection_type.name
        if self.match_protocols:
            r["match_protocols"] = [p.code for p in self.match_protocols]
        if self.allowed_params:
            r["allowed_params"] = [p.code for p in self.allowed_params]
        if self.deny_params:
            r["deny_params"] = [p.code for p in self.deny_params]
        return r


class ParamRule(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    param: "ConfigurationParam" = PlainReferenceField(ConfigurationParam)
    scope: "ConfigurationScope" = PlainReferenceField(ConfigurationScope)
    dependency_param: Optional["ConfigurationParam"] = PlainReferenceField(
        ConfigurationParam, required=False
    )
    dependency_param_values = ListField(StringField())
    is_hide = BooleanField(default=False)
    is_readonly = BooleanField(default=False)
    # Set section
    # param_helper = StringField()
    choices = ListField(StringField())

    def __str__(self):
        return "%s -> %s" % (self.param, self.choices)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "param__code": self.param.code,
            "is_hide": self.is_hide,
            "is_readonly": self.is_readonly,
        }
        if self.dependency_param:
            r["dependency_param__code"] = self.dependency_param.code
            r["dependency_param_values"] = list(self.dependency_param_values)
        if self.choices:
            r["choices"] = list(self.choices)
        return r


@on_delete_check(check=[("inv.ObjectModel", "configuration_rule")])
class ObjectConfigurationRule(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.objectconfigurationrules",
        "strict": False,
        "auto_create_index": False,
        "indexes": [],
        "json_collection": "inv.objectconfigurationrules",
        "json_unique_fields": ["name", "uuid"],
    }

    name = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    connection_rules: List["ConnectionRule"] = EmbeddedDocumentListField(ConnectionRule)
    param_rules: List["ParamRule"] = EmbeddedDocumentListField(ParamRule)

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "connection_rules": [s.json_data for s in self.connection_rules],
            "param_rules": [p.json_data for p in self.param_rules],
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "$collection", "uuid", "description", "scope_rules", "param_rules"],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def get_schema(self, param: "ConfigurationParam", o) -> Optional["ParamSchema"]:
        schema = param.get_schema(o)
        for p in self.param_rules:
            if p.param.id == param.id and p.choices:
                schema.choices = p.choices
        return schema

    def get_scope(self, param: "ConfigurationParam", oc) -> Optional[ConfigurationScope]:
        """
        Check ObjectModel Connection Match with Rule
        :param param:
        :param oc:
        :return:
        """
        protocols = set(oc.protocols)
        for rule in self.connection_rules:
            if rule.allowed_params and param not in rule.allowed_params:
                continue
            if rule.deny_params and param in rule.deny_params:
                continue
            if rule.match_context and not re.match(rule.match_context, oc.name):
                continue
            if rule.match_connection_type and rule.match_connection_type != oc.type:
                continue
            if rule.match_protocols and not set(rule.match_protocols).intersection(protocols):
                continue
            return rule.scope
        return
