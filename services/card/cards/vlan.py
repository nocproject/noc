# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VLAN card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from base import BaseCard
from noc.vc.models.vlan import VLAN


class VLANCard(BaseCard):
    name = "vlan"
    default_template_name = "vlan"
    model = VLAN

    def get_object(self, id):
        if self.current_user.is_superuser:
            return VLAN.get_by_id(id)
        else:
            return VLAN.objects.get(
                id=id,
                segment__in=self.get_user_domains()
            )

    def get_data(self):
        return {
            "object": self.object
        }
