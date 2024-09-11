# ---------------------------------------------------------------------
# Generate facade for box
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.core.svg import SVG
from .load import get_svg_for_facade
from .utils import slot_to_id
from .interaction import Interaction, InteractionAction, InteractionEvent, InteractionItem


def get_svg_for_box(
    obj: Object, name: str = "front", cache: dict[ObjectId, SVG] | None = None
) -> SVG | None:
    """
    Generate SVG for box.

    Args:
        obj: Object instance.
        name: Facade name.
    """
    cache = cache or {}
    # Get facade name
    match name:
        case "front":
            facade = obj.model.front_facade
        case "rear":
            facade = obj.model.rear_facade
        case _:
            msg = f"Invalid facade: {name}"
            raise ValueError(msg)
    # No facade?
    if not facade:
        return None
    # Get module facade
    svg = get_svg_for_facade(facade, cache=cache)
    # Insert nested modules
    for ro in obj.iter_children():
        # Always use front facades for nested modules
        mod_svg = get_svg_for_box(ro, name="front", cache=cache)
        if not mod_svg:
            continue  # Skip
        # Embed module
        try:
            svg.embed(
                slot_to_id(ro.parent_connection),
                mod_svg,
                additional=(
                    [slot_to_id(a) for a in ro.additional_connections if a]
                    if ro.additional_connections
                    else None
                ),
                interaction=Interaction(
                    actions=[
                        InteractionItem(
                            event=InteractionEvent.DBLCLICK,
                            action=InteractionAction.GO,
                            resource=ro.as_resource(),
                        )
                    ]
                ).to_str(),
            )
        except ValueError:
            pass
    return svg
