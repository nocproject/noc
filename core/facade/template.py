# ---------------------------------------------------------------------
# Generate facade template from ObjectModel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# NOC modules
from noc.inv.models.objectmodel import ObjectModel, ObjectModelConnection
from noc.inv.models.connectiontype import ConnectionType
from noc.core.svg import SVG
from .utils import name_to_id, name_to_title, slot_to_id

NS_SVG = "http://www.w3.org/2000/svg"
NS_XLINK = "http://www.w3.org/1999/xlink"
DIR_FILTER = ("i", "s")
DEFAULT_WIDTH = 20
DEFAULT_HEIGTH = 20
X_SPACE = 0
Y_SPACE = 5
RACK_WIDTH = 445
UNIT = 44.5
VERTICAL_GAP = 5.0
HORIZONTAL_GAP = 5.0


@dataclass
class ConnectionTypeInfo(object):
    """
    Various information for ConnectionType.

    Attributes:
        x: Current x position
        y: y position
        width: Width
        height: Height
        el: Element for defs, if any
    """

    x: float
    y: float
    width: float
    height: float
    el: Optional[ET.Element]

    def inc_x(self: "ConnectionTypeInfo") -> None:
        """Increase current x position to width"""
        self.x += self.width + HORIZONTAL_GAP


def get_facade_template(model: ObjectModel) -> str:
    """
    Get SVG containig facade templates for object model.
    """
    w, h = get_model_dimensions(model)
    # SVG structure and element tree
    svg = ET.Element(
        f"{{{NS_SVG}}}svg",
        {"version": "1.0", "xmlns:xlink": NS_XLINK, "viewBox": f"0 0 {w} {h}"},
    )
    tree = ET.ElementTree(svg)
    # Bounding rectanle
    rect = ET.Element(
        f"{{{NS_SVG}}}rect",
        {
            "x": "0",
            "y": "0",
            "width": str(w),
            "height": str(h),
            "style": "stroke: rgb(0, 0, 0); fill: rgb(255, 255, 255); stroke-width: 0px;",
        },
    )
    svg.append(rect)
    # Get s/i slots
    conn_types: Dict[str, ConnectionTypeInfo] = {}
    for conn in model.connections:
        # Filter proper direction
        if conn.direction not in DIR_FILTER:
            continue
        #
        ct_id = f"{name_to_id(conn.type.name)}-{conn.gender}"
        slot_id = slot_to_id(conn.name)
        # Append connnection type if necessary
        if ct_id not in conn_types:
            y = max(
                VERTICAL_GAP * len(conn_types) + sum(ct.height for ct in conn_types.values()),
                VERTICAL_GAP,
            )
            svg_el = get_connection_facade(conn)
            if svg_el:
                width = svg_el.width
                height = svg_el.height
                el = svg_el.root
                el.tag = "symbol"
                el.attrib = {"id": ct_id}
                title = ET.Element(f"{{{NS_SVG}}}title")
                title.text = name_to_title(conn.type.name)
                el.insert(0, title)
            else:
                width = DEFAULT_WIDTH
                height = DEFAULT_HEIGTH
                el = None
            conn_types[ct_id] = ConnectionTypeInfo(
                x=HORIZONTAL_GAP, y=y, width=width, height=height, el=el
            )
        # Insert element
        ct = conn_types[ct_id]
        if ct.el:
            # Has facade, use defs
            el = ET.Element(
                f"{{{NS_SVG}}}use",
                {
                    "id": slot_id,
                    "transform": f"translate({ct.x}, {ct.y})",  # move in place
                    "xlink:href": f"#{ct_id}",  # defs reference
                },
            )
        else:
            # Use rect
            el = ET.Element(
                f"{{{NS_SVG}}}rect",
                {
                    "id": slot_id,
                    "x": str(ct.x),
                    "y": str(ct.y),
                    "width": str(ct.width),
                    "height": str(ct.height),
                    "style": "stroke: rgb(0, 0, 0); fill: rgb(128, 128, 128); stroke-width: 0px;",
                },
            )
        svg.append(el)
        ct.inc_x()
    # Append defs
    if conn_types:
        el = ET.Element(f"{{{NS_SVG}}}defs")
        svg.insert(0, el)
        for ct in conn_types.values():
            if ct.el:
                el.append(ct.el)
    # Format tree
    ET.indent(tree)
    out = ET.tostring(tree.getroot(), encoding="unicode", method=None)
    return out


def get_model_dimensions(model: ObjectModel) -> Tuple[int, int]:
    """
    Get dimenstions from model.

    Args:
        model: Object Model instance

    Returns:
        width, height tuple

    Raises:
        ValueError: if dimensions cannot be deduced.
    """
    # Check we have dimensions
    w = model.get_data("dimensions", "width")
    h = model.get_data("dimensions", "height")
    units = model.get_data("rackmount", "units")
    # Try to deduce size from rack units
    if not w and units:
        w = str(RACK_WIDTH)
    if not h and units:
        ru = float(units)
        h = str(UNIT * ru)
    # Get from `o` connection type
    if not h or not w:
        ct = _get_outer_connection_type(model)
        if ct:
            if not w:
                w = ct.get_data("dimensions", "width")
            if not h:
                h = ct.get_data("dimensions", "height")
    # Check we have dimensions
    if not w or not h:
        msg = "width and height dimensions must be set"
        raise ValueError(msg)
    return w, h


def _get_outer_connection_type(model: ObjectModel) -> Optional[ConnectionType]:
    """
    Get connection type for outer connection.

    Outer connection must be single.

    Args:
        model: Object model instance.

    Returns:
        Connection type.
    """
    outers = [c for c in model.connections if c.is_outer]
    if len(outers) != 1:
        return None
    return outers[0].type


def is_valid_model_for_template(model: ObjectModel) -> bool:
    """
    Check if template may be created for model.
    """
    try:
        get_model_dimensions(model)
        return True
    except ValueError:
        return False


def get_connection_facade(conn: ObjectModelConnection) -> Optional[SVG]:
    """
    Get facade for connection.

    Args:
        conn: Connection item.

    Returns:
        SVG element, if applicable.
    """
    if conn.gender == "m":
        if conn.type.male_facade:
            return SVG.from_string(conn.type.male_facade.data)
    elif conn.gender == "f":
        if conn.type.female_facade:
            return SVG.from_string(conn.type.female_facade.data)
    else:
        if conn.type.male_facade:
            return SVG.from_string(conn.type.male_facade.data)
        if conn.type.female_facade:
            return SVG.from_string(conn.type.female_facade.data)
    return None
