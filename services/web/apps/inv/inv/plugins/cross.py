# ---------------------------------------------------------------------
# inv.inv cross plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object
from .base import InvPlugin


class CrossPlugin(InvPlugin):
    name = "cross"
    js = "NOC.inv.inv.plugins.cross.CrossPanel"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, o: Object):
        data = []
        if o.model.cross:
            data += [
                {
                    "input": c.input,
                    "input_discriminator": c.input_discriminator or "",
                    "output": c.output,
                    "output_discriminator": c.output_discriminator or "",
                    "gain_db": c.gain_db or 1.0,
                    "scope": "model",
                }
                for c in o.model.cross
            ]
        if o.cross:
            data += [
                {
                    "input": c.input,
                    "input_discriminator": c.input_discriminator or "",
                    "output": c.output,
                    "output_discriminator": c.output_discriminator or "",
                    "gain_db": c.gain_db or 1.0,
                    "scope": "object",
                }
                for c in o.cross
            ]
        return {"id": str(o.id), "name": o.name, "model": o.model.name, "data": data}
