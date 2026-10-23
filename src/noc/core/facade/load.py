# ---------------------------------------------------------------------
# inv.inv facade loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from bson import ObjectId

# NOC modules
from noc.inv.models.facade import Facade
from noc.core.svg import SVG


def get_svg_for_facade(facade: Facade, /, cache: dict[ObjectId, SVG] | None = None) -> SVG:
    """
    Get SVG for facade.

    Args:
        facade: Facade instance.
        cache: Optional cache.

    Returns:
        SVG instance.
    """
    # Try from cache
    if cache:
        svg = cache.get(facade.id)
        if svg:
            return svg.clone()
    # Serialize
    svg = SVG.from_string(facade.data)
    # Save to cache
    if cache is not None:
        cache[facade.id] = svg.clone()
    return svg
