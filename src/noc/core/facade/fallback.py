# ---------------------------------------------------------------------
# Generate facade for box
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock

# Third-party modules
from cachetools import cached

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.facade import Facade

_fallback_cache = {}
_fallback_lock = Lock()


@cached(_fallback_cache, lock=_fallback_lock)
def get_fallback_facade_for_model(model: ObjectModel) -> Facade | None:
    """
    Get fallback facade for model.

    Args:
        model: Object Model.

    Returns:
        Facade instance if found, None otherwise.
    """
    outer = model.get_outer()
    if not outer:
        return None
    if model.cr_context and model.cr_context == "XCVR":
        return _get_fallback_xcvr(model)
    return None


def _get_fallback_xcvr(model: ObjectModel) -> Facade | None:
    """
    Get fallback facade for transceiver.
    """
    # Get type
    copper_count = 0
    optical_count = 0
    form_factor: str | None = None
    for cn in model.connections:
        if cn.is_same_level:
            if cn.type.name == "Electrical | RJ45":
                copper_count += 1
            elif cn.type.name.startswith("Optical | "):
                optical_count += 1
        elif cn.is_outer:
            form_factor = cn.type.name.split("|")[-1].strip()
    if not form_factor or (not copper_count and not optical_count):
        return None
    # Match proper type
    if copper_count:
        # RJ45
        f_map = _COPPER_MAP
    elif optical_count == 1:
        # Bidi
        f_map = _BIDI_MAP
    elif optical_count == 2:
        # Duplex
        f_map = _DUPLEX_MAP
    else:
        return None
    # Find facade
    f_name = f_map.get(form_factor)
    if not f_name:
        return None
    return Facade.get_by_name(f_name)


_COPPER_MAP: dict[str, str | None] = {
    "GBIC": None,
    "SFP": None,
    "SFP+": None,
}

_BIDI_MAP: dict[str, str | None] = {
    "CFP": None,
    "CFP2": None,
    "GBIC": None,
    "QSFP+": None,
    "QSFP28": None,
    "SFP+": None,
    "SFP": None,
    "XFP": None,
}

_DUPLEX_MAP: dict[str, str | None] = {
    "CFP": None,
    "CFP2": "Transceiver | CFP2",
    "GBIC": None,
    "QSFP+": None,
    "QSFP28": "Transceiver | QSFP28 LC",
    "SFP+": "Transceiver | SFP LC",
    "SFP": "Transceiver | SFP LC",
    "XFP": None,
}
