# ---------------------------------------------------------------------
# Generate facade template from ObjectModel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.core.svg import SVG

rx_id = re.compile("[^a-z-A-Z0-9]")
PLACEHOLDER = "-"
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


def name_to_id(name: str) -> str:
    """
    Convert name to valid id.
    """
    parts = [rx_id.sub(PLACEHOLDER, x.strip()).lower() for x in name.split("|")]
    return f"noc-{PLACEHOLDER.join(parts)}"


def name_to_title(name: str) -> str:
    """
    Use last part of name as title.
    """
    return name.split("|")[-1].strip()


def slot_to_id(name: str) -> str:
    """
    Convert slot name to id.
    """
    s = rx_id.sub(PLACEHOLDER, name).lower()
    return f"slot-{s}"


def get_facade_template(model: ObjectModel) -> str:
    """
    Get SVG containig facade templates for object model.
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
    # Check we have dimensions
    if not w or not h:
        msg = "width and height dimensions must be set"
        raise ValueError(msg)
    # SVG structure and element tree
    svg = ET.Element(
        f"{{{NS_SVG}}}svg",
        {
            "version": "1.0",
            "xmlns:xlink": NS_XLINK,
            "width": f"{w}mm",
            "height": f"{h}mm",
        },
    )
    tree = ET.ElementTree(svg)
    # Outer group
    g = ET.Element("g")
    svg.append(g)
    # Bounding rectanle
    rect = ET.Element(
        f"{{{NS_SVG}}}rect",
        {
            "x": "0",
            "y": "0",
            "width": str(w),
            "height": str(h),
            "style": "stroke: rgb(0, 0, 0); fill: rgb(255, 255, 255);",
        },
    )
    g.append(rect)
    # Get s/i slots
    conn_types: Dict[str, ConnectionTypeInfo] = {}
    for conn in model.connections:
        # Filter proper direction
        if conn.direction not in DIR_FILTER:
            continue
        #
        ct_id = name_to_id(conn.type.name)
        slot_id = slot_to_id(conn.name)
        # Append connnection type if necessary
        if ct_id not in conn_types:
            y = VERTICAL_GAP * len(conn_types) + sum(ct.height for ct in conn_types.values())
            if conn.type.facade:
                svg_el = SVG.from_string(conn.type.facade.data)
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
                    "style": "stroke: rgb(0, 0, 0); fill: rgb(255, 255, 255);",
                },
            )
        g.append(el)
        ct.inc_x()
    # Append defs
    if conn_types:
        el = ET.Element(f"{{{NS_SVG}}}defs")
        svg.insert(0, el)
        for sn, d in conn_types.items():
            if d.el:
                el.append(d.el)
    # Format tree
    ET.indent(tree)
    out = ET.tostring(tree.getroot(), encoding="unicode", method=None)
    return out
