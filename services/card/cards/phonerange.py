# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PhoneRange card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.phone.models.phonenumber import PhoneNumber
from noc.phone.models.phonerange import PhoneRange

# NOC modules
from base import BaseCard


class PhoneRangeCard(BaseCard):
    name = "phonerange"
    default_template_name = "phonerange"
    model = PhoneRange

    def get_data(self):
        return {
            "object": self.object,
            "path": [PhoneRange.get_by_id(p) for p in PhoneRange.get_path(self.object)[:-1]],
            "ranges": PhoneRange.objects.filter(
                dialplan=self.object.dialplan.id,
                parent=self.object.id
            ).order_by("from_number"),
            "numbers": PhoneNumber.objects.filter(
                dialplan=self.object.dialplan.id,
                phone_range=self.object.id
            )
        }

    @classmethod
    def search(cls, handler, query):
        r = []
        for p in PhoneRange.objects.filter(
                from_number__lte=query,
                to_number__gte=query
        ).order_by("-from_number", "to_number"):
            r += [{
                "scope": "phonerange",
                "id": str(p.id),
                "label": "%s (%s - %s)" % (p.name, p.from_number, p.to_number)
            }]
        return r
