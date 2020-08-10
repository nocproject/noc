# ----------------------------------------------------------------------
# Topology types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import Enum
from dataclasses import dataclass


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
