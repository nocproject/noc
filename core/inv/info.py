# ----------------------------------------------------------------------
# Gather info for resource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Optional, Dict, Callable, List
from enum import Enum

# Python modules
from noc.inv.models.object import Object
from noc.inv.models.channel import Channel
from noc.fm.models.activealarm import ActiveAlarm, PathCode
from noc.core.feature import Feature
from noc.core.translation import ugettext as _
from noc.core.glyph import Glyph


@dataclass
class PathItem(object):
    label: str
    id: str | None = None

    def to_json(self) -> dict[str, Any]:
        """Convert PathItem to JSON-serializable dict."""
        r = {"label": self.label}
        if self.id:
            r["id"] = self.id
        return r

    @classmethod
    def from_object(cls, obj: Object) -> "list[PathItem] | None":
        """Get path for object."""
        r: list[PathItem] = []
        current = obj.parent
        while current:
            r.append(
                PathItem(
                    label=current.parent_connection if current.parent_connection else current.name,
                    id=str(current.id),
                )
            )
            # if current.is_container:
            #    break
            current = current.parent
        return list(reversed(r)) if r else None

    @classmethod
    def from_channel(cls, ch: Channel) -> "Optional[List[PathItem]]":
        """Get path for channel."""
        return [PathItem(label=ch.name, id=str(id))]


class ButtonAction(Enum):
    GO = "go"


class GoScope(Enum):
    """Scope for GO action"""

    OBJECT = "o"
    CHANNEL = "c"


@dataclass
class Button(object):
    label: str | None = None
    glyph: Glyph | None = None
    hint: str | None = None
    action: ButtonAction | None = None
    args: str | None = None
    scope: Optional[GoScope] = None

    def to_json(self) -> dict[str, str | int]:
        """Convert Button to JSON-serializable dict."""
        r: dict[str, str | int] = {}
        if self.label:
            r["label"] = self.label
        if self.glyph:
            r["glyph"] = self.glyph.value
        if self.hint:
            r["hint"] = self.hint
        if self.action:
            r["action"] = self.action.value
        if self.args:
            r["args"] = self.args
        if self.scope:
            r["scope"] = self.scope.value
        return r


@dataclass
class Info(object):
    title: str | None = None
    description: str | None = None
    path: list[PathItem] | None = None
    buttons: list[Button] | None = None
    n_alarms: Optional[int] = None

    def to_json(self) -> dict[str, Any]:
        """Convert Info to JSON-serializable dict."""
        r: dict[str, Any] = {}
        if self.title:
            r["title"] = self.title
        if self.description:
            r["description"] = self.description
        if self.path:
            r["path"] = [x.to_json() for x in self.path]
        if self.buttons:
            r["buttons"] = [x.to_json() for x in self.buttons]
        if self.n_alarms:
            r["n_alarms"] = self.n_alarms
        return r


def info(resource: str) -> Optional[Info]:
    """
    Collect info for resource.

    Args:
        resource: Resource reference.

    Returns:
        Info: with info structure.
        None: when resource cannot be dereferenced.
    """
    if ":" not in resource:
        return None
    schema = resource.split(":", 1)[0]
    handler = INFO_HANDLERS.get(schema)
    if not handler:
        return None
    return handler(resource)


def _info_for_object(resource: str) -> Optional[Info]:
    """
    Build info for object.
    """
    # Resolve object
    try:
        obj, name = Object.from_resource(resource)
        if obj is None:
            return None
    except ValueError:
        return None
    # Check for alarms
    n_alarms = None
    if Feature.FGALARMS.is_active():
        n_alarms = ActiveAlarm._get_collection().count_documents(
            {"resource_path": {"$elemMatch": {"c": PathCode.OBJECT.value, "p": resource}}}
        )
    if name:
        # info for connection
        cn = obj.model.get_model_connection(name)
        if cn and cn.type is not None:
            ct = cn.type.name.split("|")[-1].strip()
            description = ct
            if cn.is_inner:
                description += " - not connected"
        else:
            description = "Unknown connection"
        return Info(
            title=name, path=PathItem.from_object(obj), description=description, n_alarms=n_alarms
        )
    # Info for object
    return Info(
        title=obj.parent_connection if obj.parent_connection else obj.name,
        path=PathItem.from_object(obj),
        description=f"{obj.model.get_short_label()}",
        buttons=[
            Button(
                glyph=Glyph.ARROW_RIGHT,
                hint=_("Go to object"),
                action=ButtonAction.GO,
                scope=GoScope.OBJECT,
                args=str(obj.id),
            )
        ],
        n_alarms=n_alarms,
    )


def _info_for_channel(resource: str) -> Optional[Info]:
    """Build info for channel."""
    try:
        ch, _unused = Channel.from_resource(resource)
        if ch is None:
            return None
    except ValueError:
        return None
    n_alarms = None
    if Feature.FGALARMS.is_active():
        n_alarms = ActiveAlarm._get_collection().count_documents(
            {"resource_path": {"$elemMatch": {"c": PathCode.CHANNEL.value, "p": resource}}}
        )
    return Info(
        title=f"{ch.name} [{ch.tech_domain.name}]",
        path=[],
        description=ch.description or "",
        buttons=[
            Button(
                glyph=Glyph.ARROW_RIGHT,
                hint=_("Go to channel"),
                action=ButtonAction.GO,
                scope=GoScope.CHANNEL,
                args=str(ch.id),
            )
        ],
        n_alarms=n_alarms,
    )


INFO_HANDLERS: Dict[str, Callable[[str], Optional[Info]]] = {
    "o": _info_for_object,
    "c": _info_for_channel,
}
