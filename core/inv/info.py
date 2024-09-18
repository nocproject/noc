# ----------------------------------------------------------------------
# Gather info for resource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any

# Python modules
from noc.inv.models.object import Object


@dataclass
class PathItem(object):
    label: str

    def to_json(self) -> dict[str, Any]:
        """Convert PathItem to JSON-serializable dict."""
        return {"label": self.label}


@dataclass
class Button(object):
    label: str | None
    glyph: str | None

    def to_json(self) -> dict[str, Any]:
        """Convert Button to JSON-serializable dict."""
        r: dict[str, str] = {}
        if self.label:
            r["label"] = self.label
        if self.glyph:
            r["glyph"] = self.glyph
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
            PathItem(label=current.parent_connection if current.parent_connection else current.name)
        )
        if current.is_container:
            break
        current = obj.parent
    return list(reversed(r)) if r else None


def _info_for_object(obj: Object) -> Info:
    """
    Build info for object.
    """
    return Info(
        title=obj.parent_connection if obj.parent_connection else obj.name,
        path=_get_path(obj),
        description=f"{obj.model.get_short_label()}",
    )


def _info_for_connection(obj: Object, name: str) -> Info:
    """
    Build info for connection.
    """
    return Info(title=name, path=_get_path(obj))
