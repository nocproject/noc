# ----------------------------------------------------------------------
# Gather info for resource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any
from enum import Enum

# Python modules
from noc.inv.models.object import Object
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


class ButtonAction(Enum):
    GO = "go"


@dataclass
class Button(object):
    label: str | None = None
    glyph: Glyph | None = None
    hint: str | None = None
    action: ButtonAction | None = None
    args: str | None = None

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
        return r


@dataclass
class Info(object):
    title: str | None = None
    description: str | None = None
    path: list[PathItem] | None = None
    buttons: list[Button] | None = None

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
        return r


def info(resource: str) -> Info | None:
    """
    Collect info for resource.

    Args:
        resource: Resource reference.

    Returns:
        Info: with info structure.
        None: when resource cannot be dereferenced.
    """
    try:
        obj, name = Object.from_resource(resource)
        if obj is None:
            return None
    except ValueError:
        return None
    if name is None:
        return _info_for_object(obj)
    return _info_for_connection(obj, name)


def _get_path(obj: Object) -> list[PathItem] | None:
    """Get path for object."""
    if obj.is_container:
        return None
    r: list[PathItem] = []
    current = obj.parent
    while current:
        r.append(
            PathItem(
                label=current.parent_connection if current.parent_connection else current.name,
                id=str(current.id),
            )
        )
        if current.is_container:
            break
        current = current.parent
    return list(reversed(r)) if r else None


def _info_for_object(obj: Object) -> Info:
    """
    Build info for object.
    """
    return Info(
        title=obj.parent_connection if obj.parent_connection else obj.name,
        path=_get_path(obj),
        description=f"{obj.model.get_short_label()}",
        buttons=[
            Button(
                glyph=Glyph.ARROW_RIGHT,
                hint=_("Go to object"),
                action=ButtonAction.GO,
                args=str(obj.id),
            )
        ],
    )


def _info_for_connection(obj: Object, name: str) -> Info:
    """
    Build info for connection.
    """
    cn = obj.model.get_model_connection(name)
    if cn and cn.type is not None:
        ct = cn.type.name.split("|")[-1].strip()
        description = ct
    else:
        description = "Unknown connection"
    return Info(title=name, path=_get_path(obj), description=description)
