# ---------------------------------------------------------------------
# Generate facade for rack
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterable
import xml.etree.ElementTree as ET

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.core.svg import SVG
from .interaction import Interaction, InteractionAction, InteractionEvent, InteractionItem
from .box import get_svg_for_box

GOLDEN_RATIO = 1.6

# Size
UNIT = 44.75
INNER_WIDTH = 482.6  # 19"
TOP_SIZE = 70.0
BOTTOM_SIZE = 20.0
LEFT_SIZE = 50.0
RIGHT_SIZE = LEFT_SIZE
RULER_SIZE = 50.0

# Calculated sizes
TOP_LABEL_SIZE = float(int(TOP_SIZE / GOLDEN_RATIO))
TOP_GAP = (TOP_SIZE - TOP_LABEL_SIZE) / 2.0
RULER_LABEL_SIZE = float(int(UNIT / GOLDEN_RATIO))
RULER_GAP = (RULER_SIZE - RULER_LABEL_SIZE) / 2.0

# Colors
RACK_BODY_COLOR = "#000000"
RACK_BODY_LIGHT = "#95a5a6"
RACK_BODY_SHADE = "#7f8c8d"
FONT_COLOR = "#c0c0c0"
RULER_COLOR = "#202020"
INNER_COLOR = "#808080"
RULER_LINE_COLOR = "#606060"
PLACEHOLDER_COLOR = "red"
PLACEHOLDER_STROKE_COLOR = "blue"

# Labels
FONT = "Arial,sans-serif"


def get_rack_svg(units: int, title: str | None = None) -> SVG:
    """
    Generate SVG for rack of given size.

    Args:
        units: Rack size in units.
        title: Rack title.

    Returns:
        Rendered SVG instance.
    """
    svg = SVG.init()
    # Adjust size
    outer_width = LEFT_SIZE + INNER_WIDTH + RULER_SIZE + RIGHT_SIZE
    outer_height = BOTTOM_SIZE + UNIT * float(units) + TOP_SIZE
    svg.width = outer_width
    svg.height = outer_height
    # Root SVG element
    root = svg.root
    # Add gradient
    defs = ET.Element("defs")
    root.append(defs)
    grad = ET.Element("linearGradient", {"id": "rack-gradient"})
    defs.append(grad)
    for stop, color in [
        (0.0, RACK_BODY_COLOR),
        (0.3, RACK_BODY_SHADE),
        (0.375, RACK_BODY_LIGHT),
        (0.45, RACK_BODY_SHADE),
        (1.0, RACK_BODY_COLOR),
    ]:
        el = ET.Element("stop", {"offset": str(stop), "style": f"stop-color: {color}"})
        grad.append(el)
    # Add bounding box
    root.append(
        ET.Element(
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(outer_width),
                "height": str(outer_height),
                "style": "fill: url(#rack-gradient); stroke-width: 0px",
            },
        )
    )
    # Place title
    if title:
        el = ET.Element(
            "text",
            {
                "x": str(LEFT_SIZE + INNER_WIDTH + RULER_SIZE),
                "y": str(TOP_GAP + TOP_LABEL_SIZE),
                "style": "white-space:pre;"
                f"font-family: {FONT};"
                f"font-size: {int(TOP_LABEL_SIZE)}px;"
                "text-anchor: end;"
                f"fill: {FONT_COLOR}",
            },
        )
        el.text = title
        root.append(el)
    # Add inner place
    root.append(
        ET.Element(
            "rect",
            {
                "x": str(LEFT_SIZE),
                "y": str(TOP_SIZE),
                "width": str(INNER_WIDTH),
                "height": str(UNIT * float(units)),
                "style": f"fill: {INNER_COLOR}; stroke-width: 0px",
            },
        )
    )
    # Add ruler
    root.append(
        ET.Element(
            "rect",
            {
                "x": str(LEFT_SIZE + INNER_WIDTH),
                "y": str(TOP_SIZE),
                "width": str(RULER_SIZE),
                "height": str(UNIT * float(units)),
                "style": f"fill: {RULER_COLOR}; stroke-width: 0px",
            },
        )
    )
    # Add ruler delimiters
    for n in range(1, units):
        y = TOP_SIZE + n * UNIT
        root.append(
            ET.Element(
                "line",
                {
                    "x1": str(LEFT_SIZE),
                    "y1": str(y),
                    "x2": str(LEFT_SIZE + INNER_WIDTH + RULER_SIZE),
                    "y2": str(y),
                    "style": f"stroke: {RULER_LINE_COLOR}; stroke-width: 1px",
                },
            )
        )
    # Add ruler labels
    for n in range(1, units + 1):
        el = ET.Element(
            "text",
            {
                "x": str(LEFT_SIZE + INNER_WIDTH + RULER_SIZE),
                "y": str(TOP_SIZE + (units - n + 1) * UNIT - RULER_GAP),
                "style": "white-space:pre;"
                f"font-family: {FONT};"
                f"font-size: {int(RULER_LABEL_SIZE)}px;"
                "text-anchor: end;"
                f"fill: {FONT_COLOR}",
            },
        )
        el.text = str(n)
        root.append(el)
    return svg


def get_placeholder_svg(obj: Object) -> SVG:
    """
    Generape placeholder for object.

    Placeholders used when object has no facade.

    Args:
        obj: Object

    Return:
        Placeholder SVG.
    """
    # Sizes
    width = INNER_WIDTH
    height = obj.get_data("rackmount", "units") * UNIT
    # Get SVG
    svg = SVG.init()
    svg.width = width
    svg.height = height
    # Draw inner
    root = svg.root
    # Bounding rect
    root.append(
        ET.Element(
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(width),
                "height": str(height),
                "style": f"fill: {PLACEHOLDER_COLOR};"
                "stroke: {PLACEHOLDER_STORKE_COLOR};"
                "stroke-width: 1px",
            },
        )
    )
    # 1st diagonal
    root.append(
        ET.Element(
            "line",
            {
                "x1": "0",
                "y1": "0",
                "x2": str(width),
                "y2": str(height),
                "style": "stroke: {PLACEHOLDER_STORKE_COLOR}; stroke-width: 1px",
            },
        )
    )
    # 2nd diagonal
    root.append(
        ET.Element(
            "line",
            {
                "x1": "0",
                "y1": str(height),
                "x2": str(width),
                "y2": "0",
                "style": "stroke: {PLACEHOLDER_STORKE_COLOR}; stroke-width: 1px",
            },
        )
    )
    return svg


def get_svg_for_rack(obj: Object, name: str = "front") -> SVG:
    """
    Generate SVG for rack and its content.

    Args:
        obj: Rack object.
        name: View name.

    Returns:
        SVG for rack and contents.
    """

    def iter_side(side: str) -> Iterable[Object]:
        """
        Iterate objects for side.

        Args:
            side: `f` or `r`.
        """
        for child in obj.iter_children():
            if child.get_data("rackmount", "side") == side:
                yield child

    def get_y(item: Object) -> float:
        """
        Get Y coordinate for object.
        """
        size = item.get_data("rackmount", "units")
        position = item.get_data("rackmount", "position")
        shift = item.get_data("rackmount", "shift") or 0
        return TOP_SIZE + (units - size - position + 1) * UNIT - float(shift * UNIT / 3.0)

    # Get rack size
    units = obj.get_data("rack", "units")
    # Get side
    match name:
        case "front":
            near_side = "f"
            far_side = "r"
        case "rear":
            near_side = "r"
            far_side = "f"
        case _:
            raise ValueError("invalid side")

    svg = get_rack_svg(obj.get_data("rack", "units"), title=obj.name)
    # Draw far side
    cache: dict[ObjectId, SVG] = {}
    for box in iter_side(far_side):
        box_svg = get_svg_for_box(box, name="rear", cache=cache) or get_placeholder_svg(box)
        svg.place(
            box_svg,
            x=LEFT_SIZE,
            y=get_y(box),
            interaction=Interaction(
                actions=[
                    InteractionItem(
                        event=InteractionEvent.CLICK,
                        action=InteractionAction.INFO,
                        resource=box.as_resource(),
                    ),
                ]
            ).to_str(),
        )
    # Draw near side
    for box in iter_side(near_side):
        box_svg = get_svg_for_box(box, name="front", cache=cache) or get_placeholder_svg(box)
        svg.place(
            box_svg,
            x=LEFT_SIZE,
            y=get_y(box),
            interaction=Interaction(
                actions=[
                    InteractionItem(
                        event=InteractionEvent.CLICK,
                        action=InteractionAction.INFO,
                        resource=box.as_resource(),
                    ),
                ]
            ).to_str(),
        )
    return svg
