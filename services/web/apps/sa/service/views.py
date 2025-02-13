# ----------------------------------------------------------------------
# sa.service application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Optional, List, Dict

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.sa.interfaces.base import (
    UnicodeParameter,
    ModelParameter,
    DictListParameter,
    StringListParameter,
    IPv4Parameter,
)
from noc.sa.models.service import Service
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.translation import ugettext as _
from noc.core.validators import is_objectid, is_ipv4, is_mac
from noc.core.models.serviceinstanceconfig import InstanceType
from noc.core.models.inputsources import InputSource
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
        elif is_ipv4(query.strip()):
            svcs = [
                s.id
                for s in ServiceInstance.objects.filter(addresses__address=query.strip()).scalar(
                    "service"
                )
            ]
            q = Q(id__in=svcs)
        elif is_mac(query.strip()):
            svcs = [
                s.id for s in ServiceInstance.objects.filter(macs=[query.strip()]).scalar("service")
            ]
            q = Q(id__in=svcs)
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
            "address": ";".join(a.address for a in o.addresses),
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

    @view("^(?P<sid>[0-9a-f]{24})/instance/", access="read", api=True)
    def api_get_instance(self, request, sid: str):
        o = self.get_object_or_404(Service, id=sid)
        r = []
        for si in ServiceInstance.objects.filter(service=o):
            r.append(
                {
                    "sources": [
                        {"discovery": "D", "etl": "E", "manual": "M"}[ss.value] for ss in si.sources
                    ],
                    "type": si.type,
                    "fqdn": si.fqdn,
                    "port": si.port,
                    "managed_object": None,
                    "addresses": [],
                    "name": si.name,
                    "resources": [],
                    "allow_update": True,
                }
            )
            if si.managed_object:
                r[-1] |= {
                    "managed_object": si.managed_object.id,
                    "managed_object__label": si.managed_object.name,
                }
            for a in si.addresses:
                if a.pool:
                    r[-1]["addresses"] += [
                        {"address": a.address, "pool": str(a.pool.id), "pool__label": a.pool.name}
                    ]
                else:
                    r[-1]["addresses"] += [{"address": a.address, "pool": None}]
            for r in si.resources:
                r[-1]["resources"] += [{"resource": r, "resource_label": "Name1"}]
        return r

    @view(r"^(?P<sid>[0-9a-f]{24})/resource/(?P<r_type>\S+)/", access="read", api=True)
    def api_get_instance_resources(self, request, sid: str, r_type: str):
        # o = self.get_object_or_404(Service, id=sid)
        q = self.parse_request_query(request)
        if "managed_object" not in q:
            return []
        if r_type == "interface":
            r_model = Interface.objects.filter(
                managed_object=int(q["managed_object"]), type="physical"
            )
        elif r_type == "subinterface":
            r_model = SubInterface.objects.filter(managed_object=int(q["managed_object"]))
        else:
            return self.response_not_found(f"{r_type} not found")
        r = []
        for res in r_model:
            r.append(
                {
                    "resource": res.as_resource(),
                    "resource__label": str(res),
                }
            )
        return r

    @view(
        r"^(?P<sid>[0-9a-f]{24})/register_instance/(?P<i_type>\S+)/",
        method=["POST"],
        access="register_instance",
        validate={
            "name": UnicodeParameter(required=False),
            "fqdn": UnicodeParameter(required=False),
        },
        api=True,
    )
    def api_register_instance(
        self,
        request,
        sid: str,
        i_type: str,
        name: Optional[str] = None,
        fqdn: Optional[str] = None,
    ):
        o = self.get_object_or_404(Service, id=sid)
        try:
            i_type = InstanceType(i_type)
        except ValueError:
            return {"success": True, "detail": f"Not supported type: {i_type}"}
        o.register_instance(i_type, name=name, fqdn=fqdn)
        return {"success": True}

    @view(
        r"^(?P<sid>[0-9a-f]{24})/instance/(?P<iid>[0-9a-f]{24})/bind/",
        method=["PUT"],
        access="update",
        validate={
            "managed_object": ModelParameter(model=ManagedObject, required=False),
            "addresses": DictListParameter(
                required=False,
                attrs={
                    "address": IPv4Parameter(required=True),
                    "pool": UnicodeParameter(required=False),
                },
            ),
            "resources": StringListParameter(required=False),
        },
        api=True,
    )
    def api_instance_bind(
        self,
        request,
        sid: str,
        iid: str,
        managed_object: Optional[ManagedObject] = None,
        resources: List[str] = None,
        addresses: List[Dict[str, str]] = None,
    ):
        si = self.get_object_or_404(ServiceInstance, id=iid)
        if addresses:
            si.register_endpoint(InputSource.MANUAL, addresses=[a["address"] for a in addresses])
        if managed_object:
            si.refresh_managed_object(managed_object, source=InputSource.MANUAL)
        if resources:
            si.update_resources(resources, source=InputSource.MANUAL)
        return {"success": True}

    @view(
        r"^(?P<sid>[0-9a-f]{24})/instance/(?P<iid>[0-9a-f]{24})/unbind/(?P<r_type>\S+)/",
        method=["PUT"],
        access="update",
        api=True,
    )
    def api_instance_unbind(
        self,
        request,
        sid: str,
        iid: str,
        r_type: str,
    ):
        # Check Permission
        si = self.get_object_or_404(ServiceInstance, id=iid)
        if r_type == "managed_object":
            si.refresh_managed_object()
        elif r_type == "addresses":
            si.deregister_endpoint(InputSource.MANUAL)
        elif r_type == "resources":
            si.update_resources([], InputSource.MANUAL)
