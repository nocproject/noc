# ---------------------------------------------------------------------
# inv.inv conduits plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object
from .base import InvPlugin


class CommutationPlugin(InvPlugin):
    name = "commutation"
    js = "NOC.inv.inv.plugins.commutation.CommutationPanel"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, object):
        return {"dot": self.get_dot(object)}

    def get_dot(self, object: Object) -> str:
        r = ["graph {", "A -- B", "}"]
        return "\n".join(r)
