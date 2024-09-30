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
    if obj.is_xcvr:
        return svg  # Do not mark transceiver pins
    # Get nested modules
    children = {
        child.parent_connection: child for child in obj.iter_children() if child.parent_connection
    }
    # Iterate through connections
    for c in obj.model.connections:
        if c.is_outer:
            continue
        slot_id = slot_to_id(c.name)
        child = children.get(c.name)
        if not child:
            # Mark connection
            interaction = Interaction(
                actions=[
                    InteractionItem(
                        event=InteractionEvent.CLICK,
                        action=InteractionAction.INFO,
                        resource=f"o:{obj.id}:{c.name}",
                    )
                ]
            )
            svg.set(slot_id, "data-interaction", interaction.to_str())
            svg.add_class(slot_id, svg.SELECTABLE_CLS)
            continue
        # Nested module
        # Always use front facades for nested modules
        mod_svg = get_svg_for_box(child, name="front", cache=cache)
        if not mod_svg:
            continue  # @todo: Generate placeholder
        # Embed module
        try:
            svg.embed(
                slot_id,
                mod_svg,
                additional=(
                    [slot_to_id(a) for a in child.additional_connections if a]
                    if child.additional_connections
                    else None
                ),
                interaction=Interaction(
                    actions=[
                        InteractionItem(
                            event=InteractionEvent.CLICK,
                            action=InteractionAction.INFO,
                            resource=child.as_resource(),
                        ),
                    ]
                ).to_str(),
            )
        except ValueError:
            pass
    return svg
