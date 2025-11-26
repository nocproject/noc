# ----------------------------------------------------------------------
# CapsItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, List, Optional

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DynamicField, BooleanField
from pydantic import BaseModel

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.caps.types import CapsConfig
from .capability import Capability


class CapsItem(EmbeddedDocument):
    capability: Capability = PlainReferenceField(Capability)
    value = DynamicField()
    # Source name like "caps", "interface", "manual"
    source = StringField()
    scope = StringField()

    def __str__(self):
        if self.scope:
            return f"{self.capability.name}@{self.scope} = {self.value}"
        return f"{self.capability.name} = {self.value}"

    @classmethod
    def get_caps(cls, *args: List["CapsItem"], scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.

        :param args:
        :param scope: Scope Name
        :return:
        """
        r: Dict[str, Any] = {}
        for caps in args:
            for ci in caps:
                cn = ci.capability.name
                if cn in r and (not scope or ci.scope != scope):
                    continue
                r[cn] = ci.value
        return r

    def clean(self):
        if self.capability:
            self.value = self.capability.clean_value(self.value)


class ModelCapsItem(BaseModel):
    capability: str
    value: Any
    # Source name like "caps", "interface", "manual"
    source: str = "manual"
    scope: Optional[str] = ""

    def __str__(self):
        return self.capability.name

    @classmethod
    def get_caps(cls, *args: List["CapsItem"]) -> Dict[str, Any]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.

        :param args:
        :return:
        """
        r: Dict[str, Any] = {}
        for caps in args:
            for ci in caps:
                cn = ci.capability.name
                if cn in r:
                    continue
                r[cn] = ci.value
        return r

    def clean(self):
        if self.capability:
            self.value = self.capability.clean_value(self.value)


class CapsSettings(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    # Required
    capability: Capability = PlainReferenceField(Capability, required=True)
    default_value = DynamicField()
    allow_manual = BooleanField(default=False)
    ref_scope = StringField(required=False)
    # ref_remote_system

    def __str__(self):
        return f"{self.capability.name}: D:{self.default_value}; M: {self.allow_manual}"

    def clean(self):
        super().clean()
        if self.default_value:
            self.capability.clean_value(self.default_value)

    def get_config(self) -> CapsConfig:
        """"""
        return CapsConfig(
            default_value=self.default_value or None,
            allow_manual=self.allow_manual,
            ref_scope=self.ref_scope,
        )
