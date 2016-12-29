# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PhoneNumber card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseCard
from noc.phone.models.phonerange import PhoneRange
from noc.phone.models.phonenumber import PhoneNumber


class PhoneNumberCard(BaseCard):
    name = "phonenumber"
    default_template_name = "phonenumber"
    model = PhoneNumber

    def get_data(self):
        return {
            "object": self.object,
            "path": [PhoneRange.get_by_id(p)
                     for p in PhoneRange.get_path(self.object.phone_range)],
        }

    @classmethod
    def search(cls, handler, query):
        r = []
        for p in PhoneNumber.objects.filter(
            number=query
        ):
            r += [{
                "scope": "phonenumber",
                "id": str(p.id),
                "label": "%s: %s" % (p.dialplan.name, p.number)
            }]
        return r
