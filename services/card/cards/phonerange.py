# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PhoneRange card handler
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


class PhoneRangeCard(BaseCard):
    name = "phonerange"
    default_template_name = "phonerange"
    model = PhoneRange

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
            ),
            "service_groups": service_groups,
            "client_groups": client_groups
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
