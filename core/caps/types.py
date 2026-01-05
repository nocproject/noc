# ----------------------------------------------------------------------
# Capabilities types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Any, List

# NOC modules
from noc.core.models.valuetype import ValueType
from noc.core.models.inputsources import InputSource


@dataclass(frozen=True)
class CapsConfig(object):
    allow_manual: bool = False
    default_value: Optional[Any] = None
    ref_scope: Optional[str] = None
    set_label: Optional[str] = None


@dataclass(frozen=True)
class CapsValue(object):
    capability: Any
    value: Any
    source: InputSource
    scope: Optional[str] = None
    config: CapsConfig = CapsConfig()

    def __str__(self):
        if self.scope:
            return f"{self.capability.name}@{self.scope} = {self.value}"
        return f"{self.capability.name} = {self.value}"

    @property
    def name(self) -> str:
        return self.capability.name

    def set_value(self, value: Any) -> "CapsValue":
        """Update value"""
        return CapsValue(
            capability=self.capability,
            value=value,
            source=self.source,
            scope=self.scope,
        )

    def get_form(self, allow_manual: bool = False):
        """Render Caps Form"""
        return {
            "capability": self.capability.name,
            "id": str(self.capability.id),
            # "object": str(o.id),
            "description": self.capability.description,
            "type": self.capability.type.value,
            "value": self.value,
            "source": self.source,
            "scope": self.scope or "",
            "editor": self.capability.get_editor() if self.config.allow_manual else None,
        }

    def get_labels(self) -> Optional[List[str]]:
        """Get caps Label"""
        if not self.config.set_label:
            return None
        if self.capability.multi:
            return [f"{self.config.set_label[:-1]}{v}" for v in self.value]
        if self.capability.type == ValueType.BOOL:
            if not self.value or self.config.set_label[-1] == "*":
                return None
            return [self.config.set_label]
        return [f"{self.config.set_label[:-1]}{self.value}"]
