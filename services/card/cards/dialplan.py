# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DialPlan card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.phone.models.dialplan import DialPlan
from noc.phone.models.phonerange import PhoneRange

# NOC modules
from base import BaseCard


class DialPlanCard(BaseCard):
    name = "dialplan"
    default_template_name = "dialplan"
    model = DialPlan

    def get_data(self):
        return {
            "object": self.object,
            "ranges": PhoneRange.objects.filter(
                dialplan=self.object.id,
                parent__exists=False
            ).order_by("from_number")
        }
