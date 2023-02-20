# ---------------------------------------------------------------------
# CPE card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseCard
from noc.inv.models.cpe import CPE


class CPECard(BaseCard):
    name = "cpe"
    default_template_name = "cpe"
    model = CPE

    def get_object(self, id):
        return CPE.objects.get(id=id)

    def get_data(self):
        if not self.object:
            return None

        return {
            "object": self.object,
            "id": self.object.id,
            "name": self.object.name,
            "controller": self.object.controller,
        }
