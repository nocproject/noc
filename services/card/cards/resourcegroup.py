# ---------------------------------------------------------------------
# ResourceGroup card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup
from noc.models import get_model
from noc.core.comp import smart_text
from .base import BaseCard


class ResourceGroupCard(BaseCard):
    name = "resourcegroup"
    default_template_name = "resourcegroup"
    model = ResourceGroup

    CARD_MAP = {
        "inv.Interface": "interface",
        "sa.ManagedObject": "managedobject",
        "phone.PhoneRange": "phonerange",
        "phone.PhoneNumber": "phonenumber",
    }

    def get_data(self):
        # Servers
        if self.object.technology.service_model:
            services = []
            s_model = get_model(self.object.technology.service_model)
            card = self.get_card_name(self.object.technology.service_model)
            for i in s_model.objects.filter(
                effective_service_groups__overlap=[str(self.object.id)]
            ):
                services += [{"id": i.id, "card": card, "label": smart_text(i)}]
        else:
            services = []
        # Clients
        if self.object.technology.client_model:
            clients = []
            c_model = get_model(self.object.technology.client_model)
            card = self.get_card_name(self.object.technology.client_model)
            for i in c_model.objects.filter(effective_client_groups__overlap=[str(self.object.id)]):
                clients += [{"id": i.id, "card": card, "label": smart_text(i)}]
        else:
            clients = []
        # Data
        r = {
            "object": self.object,
            "technology": self.object.technology,
            "allow_services": bool(self.object.technology.service_model),
            "allow_clients": bool(self.object.technology.client_model),
            "services": services,
            "clients": clients,
            "children": [],
        }
        # Append children
        for rg in ResourceGroup.objects.filter(parent=self.object.id).order_by("name"):
            r["children"] += [rg]
        return r

    def get_card_name(self, model):
        return self.CARD_MAP[model]
