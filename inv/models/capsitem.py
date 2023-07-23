# ----------------------------------------------------------------------
# CapsItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict, List, Optional

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DynamicField, ReferenceField
from pydantic import BaseModel

# NOC modules
from .capability import Capability


class CapsItem(EmbeddedDocument):
    capability = ReferenceField(Capability)
    value = DynamicField()
    # Source name like "caps", "interface", "manual"
    source = StringField()
    scope = StringField()

    def __str__(self):
        return self.capability.name

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
