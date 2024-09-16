# ---------------------------------------------------------------------
# Attach to container
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object
from ..result import Result


def attach(container: Object, item: Object) -> Result:
    """
    Insert item into container.

    Args:
        container: Container object.
        item: attached item.
    """
    item.put_into(container)
    return Result(status=True, message="Item moved")
