# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.core.topology.path import get_shortest_path


class PathCard(BaseCard):
    name = "path"
    default_template_name = "path"

    def get_data(self):
        mo1, mo2 = [ManagedObject.get_by_id(int(x)) for x in self.id.split("-")]
        path = []
        for mo in get_shortest_path(mo1, mo2):
            path += [{
                "object": mo
            }]

        return {
            "mo1": mo1,
            "mo2": mo2,
            "path": path
        }
