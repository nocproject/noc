# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PhoneNumber card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup
from noc.phone.models.phonerange import PhoneRange
from noc.phone.models.phonenumber import PhoneNumber
from .base import BaseCard


class PhoneNumberCard(BaseCard):
    name = "phonenumber"
    default_template_name = "phonenumber"
    model = PhoneNumber

    def get_data(self):
        # Resource groups
        # Service groups (i.e. server)
        static_services = set(self.object.static_service_groups)
        service_groups = []
        for rg_id in self.object.effective_service_groups:
            rg = ResourceGroup.get_by_id(rg_id)
            service_groups += [{
                "id": rg_id,
                "name": rg.name,
                "technology": rg.technology,
                "is_static": rg_id in static_services
            }]
        # Client groups (i.e. client)
        static_clients = set(self.object.static_client_groups)
        client_groups = []
        for rg_id in self.object.effective_client_groups:
            rg = ResourceGroup.get_by_id(rg_id)
            client_groups += [{
                "id": rg_id,
                "name": rg.name,
                "technology": rg.technology,
                "is_static": rg_id in static_clients
            }]

        linked_by = []
        for n in PhoneNumber.objects.filter(linked_numbers__number=self.object.id):
            for ln in n.linked_numbers:
                if ln.number.id == self.object.id:
                    ln.number = n
                    linked_by += [ln]
        return {
            "object": self.object,
            "path": [PhoneRange.get_by_id(p)
                     for p in PhoneRange.get_path(self.object.phone_range)],
            "linked_by": linked_by,
            "service_groups": service_groups,
            "client_groups": client_groups
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
