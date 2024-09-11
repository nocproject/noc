# ---------------------------------------------------------------------
# Markup for interaction in facades
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote


class InteractionEvent(Enum):
    """
    Triggering UI event.

    Attributes:
        CLICK: click.
        DBLCLICK: double click.
    """

    CLICK = "click"
    DBLCLICK = "dblclick"
    RCLICK = "rclick"


class InteractionAction(Enum):
    """
    UI event.

    Attributes:
        INFO: Show information baloon.
        GO: Go to the resource.
    """

    INFO = "info"
    GO = "go"


@dataclass
class InteractionItem(object):
    """
    Single interaction.

    Attributes:
        event: UI event.
        action: Required action.
        resource: Related resource.
    """

    event: InteractionEvent
    action: InteractionAction
    resource: str

    def to_str(self) -> str:
        """Serialize to string."""
        return f"{self.event.value}:{self.action.value}:{quote(self.resource)}"


@dataclass
class Interaction(object):
    actions: list[InteractionItem]

    def to_str(self) -> str:
        """Serialize to string."""
        return ",".join(a.to_str() for a in self.actions)
