# ---------------------------------------------------------------------
# SVG utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ET
from typing import Type, Optional, Dict, Tuple, TextIO, Union
from io import StringIO
from copy import deepcopy
from itertools import zip_longest
from pathlib import Path


class SVG(object):
    DEFS = "{http://www.w3.org/2000/svg}defs"
    NAMESPACES = {
        "": "http://www.w3.org/2000/svg",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    def __init__(self: "SVG") -> None:
        self._tree: ET.ElementTree
        self._defs: Dict[str, ET.Element] = {}

    @classmethod
    def read(cls: Type["SVG"], fp: TextIO) -> "SVG":
        svg = SVG()
        svg._tree = cls.parse(fp)
        return svg

    @classmethod
    def from_string(cls: Type["SVG"], data: str) -> "SVG":
        return cls.read(StringIO(data))

    @classmethod
    def from_file(cls: Type["SVG"], path: Union[str, Path]) -> "SVG":
        with open(path) as fp:
            return cls.read(fp)

    def to_string(self: "SVG") -> str:
        ET.indent(self._tree)
        return ET.tostring(self._tree.getroot(), encoding="unicode", method=None)

    @classmethod
    def parse(cls: Type["SVG"], fp: TextIO) -> ET.ElementTree:
        try:
            return ET.parse(fp, parser=cls.get_parser())
        except ET.ParseError as e:
            raise ValueError(str(e)) from e

    @classmethod
    def get_parser(cls: Type["SVG"]) -> ET.XMLParser:
        return ET.XMLParser()

    def clone(self: "SVG") -> "SVG":
        svg = SVG()
        svg._tree = deepcopy(self._tree)
        return svg

    def get_tree(self: "SVG") -> ET.ElementTree:
        return self._tree

    @staticmethod
    def is_equal(e1: ET.Element, e2: ET.Element) -> bool:
        """
        Compare two elements.

        Args:
            e1: First Element.
            e2: Second Element.

        Returns:
            True, if both elements are equal
        """
        if id(e1) == id(e2):
            return True
        if e1.tag != e2.tag:
            return False
        if e1.attrib != e2.attrib:
            return False
        for c1, c2 in zip_longest(e1, e2):
            if c1 is None or c2 is None:
                return False
            if not SVG.is_equal(c1, c2):
                return False
        return True

    def get_defs(self: "SVG") -> Optional[ET.Element]:
        return self._tree.find(self.DEFS)

    def append_def(self: "SVG", el: ET.Element) -> None:
        # Check id
        el_id = el.get("id")
        if not el_id:
            return  # Should raise un error?
        # Find defs node
        defs = self.get_defs()
        if defs and not self._defs:
            # Index existing defs
            self._defs = {c.get("id", ""): c for c in defs}
        if defs:
            # Check defs is already exists
            if el_id in self._defs and self.is_equal(self._defs[el_id], el):
                return  # Already exists
        else:
            # Create defs element
            defs = ET.Element(self.DEFS)
            self._tree.getroot().insert(0, defs)
        # Append defs
        defs.append(el)
        self._defs[el_id] = el

    def validate(self: "SVG") -> None: ...

    def embed(self: "SVG", element_id: str, source: "SVG") -> None:
        source = source.clone()
        # Find node
        el = self._tree.find(f".//*[@id='{element_id}']")
        if el is None:
            msg = "Slot not found"
            raise ValueError(msg)
        # Merge defs
        src_defs = source.get_defs()
        if src_defs:
            for c in src_defs:
                self.append_def(c)
            # Remove defs from source
            source._tree.getroot().remove(src_defs)
        # Get transform attributes
        attrs = {"transform": self.get_transform(el)}
        # Add id if present
        el_id = el.get("id")
        if el_id:
            attrs["id"] = el_id
        # Remove all children from elements
        el.clear()
        # Replace with `g`
        el.tag = "g"
        el.attrib = attrs
        # Extend with content from source
        src = source.clone()
        src.add_prefix(f"{element_id}-")
        for c in src._tree.getroot():
            el.append(c)

    def add_prefix(self: "SVG", prefix: str) -> None:
        def _add_prefix(el: ET.Element) -> None:
            el_id = el.get("id")
            if el_id:
                el.set("id", f"{prefix}{el_id}")
            for c in el:
                _add_prefix(c)

        _add_prefix(self._tree.getroot())

    @classmethod
    def get_transform_origin(cls: Type["SVG"], el: ET.Element) -> Optional[Tuple[float, float]]:
        """
        Calculate effective transform origin for element.

        Args:
            el: Element

        Retuns:
            * (x, y) for transform origin.
            * None, if transform origin is not set.
        """
        style = el.get("style")
        if not style:
            return None
        for si in style.split(";"):
            si = si.strip()
            if si.startswith("transform-origin:"):
                tx, ty = si[17:].strip().split()
                # @todo: left, right, centre.
                if tx.endswith("%"):
                    x = float(el.get("x", "0"))
                    w = float(el.get("width", "0"))
                    etx = x + w * float(tx[:-1]) / 100.0
                elif tx.endswith("px"):
                    etx = float(tx[:-2])
                else:
                    etx = float(tx)
                if ty.endswith("%"):
                    y = float(el.get("y", "0"))
                    h = float(el.get("height", "0"))
                    ety = y + h * float(ty[:-1]) / 100.0
                elif ty.endswith("px"):
                    ety = float(ty[:-2])
                else:
                    ety = float(ty)
                return etx, ety
        return None

    @classmethod
    def get_transform(cls: Type["SVG"], source: ET.Element) -> str:
        def translate(x: float, y: float) -> Optional[str]:
            """
            Get `translate` transform code.
            """

            def f(x: float) -> str:
                if x.is_integer():
                    return str(int(x))
                return str(x)

            return f"translate({f(x)}, {f(y)})"

        # Get X and Y coordinates
        x = float(source.get("x", "0"))
        y = float(source.get("y", "0"))
        # Check if transform-origin is set
        transform_origin = cls.get_transform_origin(source)
        if transform_origin:
            o_x, o_y = transform_origin
            # Use origin as real coordinates
            start_transform = translate(o_x, o_y)
            # Final delta transform to compensate shift
            end_transform = translate(x - o_x, y - o_y)
        else:
            start_transform = translate(x, y)
            end_transform = None
        # Process existing transform tag
        tag_transform = source.get("transform")
        # Collect all together
        return " ".join(x for x in (start_transform, tag_transform, end_transform) if x)


# WARNING: Modifying global state
# MUST find proper solution
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
