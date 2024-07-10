# ----------------------------------------------------------------------
# sa.service application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.sa.models.service import Service
from noc.sa.models.serviceinstance import ServiceInstance
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.translation import ugettext as _
from noc.core.validators import is_objectid
from noc.core.comp import smart_text


@state_handler
class ServiceApplication(ExtDocApplication):
    """
    Service application
    """

    title = "Services"
    menu = [_("Services")]
    model = Service
    parent_model = Service
    parent_field = "parent"
    query_fields = [
        "address__contains",
        "description__icontains",
        "name_template__icontains",
        "remote_id",
    ]

    resource_group_fields = [
        "static_service_groups",
        "effective_service_groups",
        "static_client_groups",
        "effective_client_groups",
    ]

    def field_label(self, o):
        return o.label

    def bulk_field_instances(self, data):
        """
        Apply interface_count fields
        :param data:
        :return:
        """
        svc_ids = [x["id"] for x in data]
        if not svc_ids:
            return data
        instances = defaultdict(list)
        for si in ServiceInstance.objects.filter(service__in=svc_ids):
            instances[str(si.service.id)].append(self.service_instance_to_dict(si))
        # Apply service instance
        for x in data:
            x["instances"] = instances.get(x["id"]) or []
        return data

    def get_Q(self, request, query):
        if is_objectid(query):
            q = Q(id=query)
        else:
            q = super().get_Q(request, query)
        return q

    def instance_to_dict(self, o, fields=None, nocustom=False):
        def sg_to_list(items):
            return [
                {"group": str(x), "group__label": smart_text(ResourceGroup.get_by_id(x))}
                for x in items
            ]

        data = super().instance_to_dict(o, fields, nocustom)
        # Expand resource groups fields
        for fn in self.resource_group_fields:
            data[fn] = sg_to_list(data.get(fn) or [])
        if isinstance(o, Service):
            data["in_maintenance"] = o.in_maintenance
            data["service_path"] = [str(sp) for sp in data["service_path"]]
        return data

    @staticmethod
    def service_instance_to_dict(o: "ServiceInstance"):
        r = {
            "name": o.name,
            "address": o.address,
            "port": o.port,
            "fqdn": o.fqdn,
        }
        if o.managed_object:
            r["managed_object"] = o.managed_object.id
            r["managed_object__label"] = str(o.managed_object.name)
        return r

    def clean(self, data):
        # Clean resource groups
        for fn in self.resource_group_fields:
            if fn.startswith("effective_") and fn in data:
                del data[fn]
                continue
            data[fn] = [x["group"] for x in (data.get(fn) or [])]
        # Clean other
        return super().clean(data)

    @view("^(?P<id>[0-9a-f]{24})/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(Service, id=id)
        path = [Service.get_by_id(ns) for ns in o.get_path()]
        return {
            "data": [
                {"level": level + 1, "id": str(p.id), "label": smart_text(p)}
                for level, p in enumerate(path)
            ]
        }
