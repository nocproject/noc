# ---------------------------------------------------------------------
# Clear local ADM-200 crossings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import uuid

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object

ADM200 = uuid.UUID("1187f420-fa75-4701-9e7a-816f5923203b")


def fix() -> None:
    om = ObjectModel.objects.get(uuid=ADM200)
    for obj in Object.objects.filter(model=om):
        if not obj.cross:
            obj.cross = None
            obj.save()
