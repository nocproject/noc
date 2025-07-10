# ----------------------------------------------------------------------
# Capabilities types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Any
from noc.core.models.inputsources import InputSource


@dataclass(frozen=True)
class CapsValue(object):
    capability: Any
    value: Any
    source: InputSource
    scope: Optional[str] = None

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

    def get_form(self):
        """Render Caps Form"""
        return {
            "capability": self.capability.name,
            "id": str(self.capability.id),
            # "object": str(o.id),
            "description": self.capability.description,
            "type": self.capability.type,
            "value": self.value,
            "source": self.source,
            "scope": self.scope or "",
            "editor": self.capability.get_editor() if self.capability.allow_manual else None,
        }
