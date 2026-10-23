# ----------------------------------------------------------------------
# Topology types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import Enum, StrEnum
from dataclasses import dataclass
from typing import Any


class Layout(StrEnum):
    Manual = "M"
    Force_Auto = "FA"  # Always rebuild layout hints
    Auto = "A"
    Force_Spring = "FS"


class ShapeOverlayPosition(StrEnum):
    NW = "NW"
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"


class ShapeOverlayForm(StrEnum):
    Circle = "c"
    Square = "s"


@dataclass
class ShapeOverlay:
    code: str
    position: ShapeOverlayPosition = ShapeOverlayPosition.SE
    form: ShapeOverlayForm = ShapeOverlayForm.Circle


@dataclass
class MapItem:
    title: str
    id: str
    generator: str
    has_children: bool = False
    only_container: bool = False
    code: str | None = None


@dataclass
class MapSize:
    width: int | None = None
    height: int | None = None


@dataclass
class BackgroundImage:
    image: str
    opacity: int = 30


@dataclass
class PathItem:
    title: str
    id: str
    level: 0


@dataclass
class Portal:
    generator: str
    id: str | None = None
    settings: dict[str, Any] | None = None


class TopologyNodeType(Enum):
    OBJECTGROUP = "objectgroup"
    MANAGEDOBJECT = "managedobject"
    OBJECTSEGMENT = "objectsegment"
    CPE = "cpe"
    CONTAINER = "container"
    OTHER = "other"


@dataclass
class TopologyNode:
    id: str
    type: TopologyNodeType = TopologyNodeType.OTHER
    resource_id: str | None = None
    parent: str | None = None  # group node_id link
    # Title settings
    title: str | None = ""
    title_position: ShapeOverlayPosition | None = ShapeOverlayPosition.S
    title_metric_template: str | None = ""
    glyph: int | None = None
    overlays: list[ShapeOverlay] | None = None
    portal: Portal | None = None
    level: int = 25
    attrs: dict[str, Any] | None = None
    object_filter: dict[str, Any] | None = None
    caps: dict[str, Any] | None = None

    def get_attr(self) -> dict[str, Any]:
        return self.attrs or {}

    def get_caps(self) -> dict[str, Any]:
        return self.caps or {}


@dataclass
class MapMeta:
    title: str
    image: BackgroundImage | None = None
    width: int | None = None
    height: int | None = None
    layout: Layout = Layout("A")
    object_status_refresh_interval: int = 60
    max_links: int = 1000
