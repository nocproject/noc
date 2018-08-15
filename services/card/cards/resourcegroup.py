# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ResourceGroup card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup
from noc.models import get_model
from .base import BaseCard


class ResourceGroupCard(BaseCard):
    name = "resourcegroup"
    default_template_name = "resourcegroup"
    model = ResourceGroup

    CARD_MAP = {
        "sa.ManagedObject": "managedobject"
    }

    def get_data(self):
        # Servers
        if self.object.technology.service_model:
            services = []
            s_model = get_model(self.object.technology.service_model)
            card = self.get_card_name(self.object.technology.service_model)
            for i in s_model.objects.filter(effective_service_groups=str(self.object.id)):
                services += [{
                    "id": i.id,
                    "card": card,
                    "label": unicode(i)
                }]
        else:
            services = []
        # Clients
        if self.object.technology.client_model:
            clients = []
            c_model = get_model(self.object.technology.client_model)
            card = self.get_card_name(self.object.technology.client_model)
            for i in c_model.objects.filter(effective_client_groups=str(self.object.id)):
                clients += [{
                    "id": i.id,
                    "card": card,
                    "label": unicode(i)
                }]
        else:
            clients = []
        # Data
        r = {
            "object": self.object,
            "technology": self.object.technology,
            "allow_services": bool(self.object.technology.service_model),
            "allow_clients": bool(self.object.technology.client_model),
            "services": services,
            "clients": clients
        }
        # @todo: Children
        return r

    def get_card_name(self, model):
        return self.CARD_MAP[model]
