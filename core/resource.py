# ---------------------------------------------------------------------
# Resource manipulating attributes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Tuple, Optional, Union

# Third-party modules
from mongoengine.document import Document
from django.db.models import Model

# NOC modules
from noc.models import RESOURCE_MODELS, get_model


def from_resource(resource: str) -> Tuple[Union[Model, Document], Optional[str]]:
    """
    Get database item from resource.

    Args:
        resource: resource reference

    Returns:
        Tuple of item and optional connection name

    Raises:
        ValueError: on invalid reference format
        KeyError: on dereference error
    """
    parts = resource.split(":", 3)
    if len(parts) < 2:
        msg = "Resource reference is too short"
        raise ValueError(msg)
    # Get model
    model_id = RESOURCE_MODELS.get(parts[0])
    if not model_id:
        msg = f"Unknown resource model `{parts[0]}`"
        raise ValueError(msg)
    model = get_model(model_id)
    # Dereference item
    item = model.get_by_id(parts[1])
    if not item:
        msg = f"Cannot dererence `{parts[2]}`"
        raise KeyError(msg)
    if len(parts) == 2:
        # Reference to item
        return item, None
    # Reference to subcomponent
    return item, parts[2]


def resource_label(resource: str) -> str:
    """
    Convert resource to human-readable label.

    Resolve through resource model's
    `.resource_label` method, if exists.
    Otherwise use `str()`

    Args:
        resource: Resource reference

    Returns:
        Formatted label.
    """
    item, part = from_resource(resource)
    if hasattr(item, "resource_label"):
        rl = item.resource_label()
    else:
        rl = str(item)
    if part:
        return f"{rl} @ {part}"
    return rl


def resource_path(resource: str) -> list[str] | None:
    """
    Get path for resource.

    Args:
        resource: Current resource.

    Returns:
        Path to the resource or None.
    """
    if not resource.startswith("o:"):
        return [resource]
    obj, name = from_resource(resource)
    if not obj:
        return None
    return obj.as_resource_path(name)
