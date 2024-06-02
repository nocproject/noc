# ----------------------------------------------------------------------
# Topology types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal


class Layout(str, Enum):
    Manual = "M"
    Force_Auto = "FA"  # Always rebuild layout hints
    Auto = "A"
    Force_Spring = "FS"


class ShapeOverlayPosition(str, Enum):
    NW = "NW"
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"


class ShapeOverlayForm(str, Enum):
    Circle = "c"
    Square = "s"


@dataclass
class ShapeOverlay(object):
    code: str
    position: ShapeOverlayPosition = ShapeOverlayPosition.SE
    form: ShapeOverlayForm = ShapeOverlayForm.Circle


@dataclass
class MapItem(object):
    title: str
    id: str
    generator: str
    has_children: bool = False
    only_container: bool = False
    code: Optional[str] = None


@dataclass
class MapSize(object):
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class BackgroundImage(object):
    image: str
    opacity: int = 30


@dataclass
class PathItem(object):
    title: str
    id: str
    level: 0


@dataclass
class Portal(object):
    generator: str
    id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


@dataclass
class TopologyNode(object):
    id: str
    type: Literal[
        "objectgroup",
        "managedobject",
        "objectsegment",
        "cpe",
        "container",
        "other",
    ] = "other"
    resource_id: Optional[str] = None
    # Ссылка на node_id группы
    parent: Optional[str] = None
    # Подпись
    title: Optional[str] = ""
    title_position: Optional[ShapeOverlayPosition] = "S"
    title_metric_template: Optional[str] = ""
    #
    stencil: Optional[str] = None
    overlays: List[ShapeOverlay] = None
    #
    portal: Optional[Portal] = None
    level: int = 25
    attrs: Optional[Dict[str, Any]] = None
    #
    object_filter: Optional[Dict[str, Any]] = None

    def get_attr(self) -> Dict[str, Any]:
        return self.attrs or {}

    def get_caps(self):
        return {}


@dataclass
class MapMeta(object):
    title: str
    image: Optional[BackgroundImage] = None
    width: Optional[int] = None
    height: Optional[int] = None
    layout: Layout = Layout("A")
    object_status_refresh_interval: int = 60
    max_links: int = 1000
