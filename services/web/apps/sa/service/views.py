# ----------------------------------------------------------------------
# sa.service application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Any

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.services.web.base.decorators.caps import capabilities_handler
from noc.services.web.base.decorators.watch import watch_handler
from noc.sa.interfaces.base import (
    UnicodeParameter,
    ModelParameter,
    DictListParameter,
    StringListParameter,
    IntParameter,
    IPv4Parameter,
    DictParameter,
)
from noc.sa.models.service import Service
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.main.models.notificationgroup import NotificationGroup
from noc.core.middleware.tls import get_user
from noc.core.translation import ugettext as _
from noc.core.validators import is_objectid, is_ipv4, is_mac
from noc.core.models.serviceinstanceconfig import InstanceType
from noc.core.models.inputsources import InputSource
from noc.core.resource import from_resource
from noc.core.comp import smart_text


@watch_handler
@capabilities_handler
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

    def bulk_field_instance_count(self, data):
        svc_ids = [x["id"] for x in data]
        if not svc_ids:
            return data
        instances = ServiceInstance.objects.filter(service__in=svc_ids).item_frequencies("service")
        instances = {str(k): v for k, v in instances.items()}
        # Apply service instance
        for x in data:
            x["instance_count"] = instances.get(x["id"]) or 0
        return data

    def bulk_field_allow_subscribe(self, data):
        svc_ids = [x["id"] for x in data]
        if not svc_ids:
            return data
        # Check allowed subscription
        us = NotificationGroup.get_groups_by_user(get_user())
        watchers = NotificationGroup.get_user_subscriptions(get_user(), "sa.Service")
        # Apply service instance, and message Type
        for x in data:
            if us and x["id"] in watchers:
                x["allow_subscribe"] = "me"
            elif us:
                x["allow_subscribe"] = "group"
            else:
                x["allow_subscribe"] = "no"
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

    def instance_to_dict_si(self, o: ServiceInstance) -> Dict[str, Any]:
        r = {
            "id": str(o.id),
            "sources": [
                {"discovery": "D", "etl": "E", "manual": "M"}[ss.value] for ss in o.sources
            ],
            "type": o.type,
            "fqdn": o.fqdn,
            "port": o.port,
            "managed_object": None,
            "addresses": [],
            "name": o.name,
            "resources": [],
            "allow_update": o.type != InstanceType.OTHER,
        }
        if o.managed_object:
            r |= {
                "managed_object": o.managed_object.id,
                "managed_object__label": o.managed_object.name,
            }
        for a in o.addresses:
            if a.pool:
                r["addresses"] += [
                    {"address": a.address, "pool": str(a.pool.id), "pool__label": a.pool.name}
                ]
            else:
                r["addresses"] += [{"address": a.address, "pool": None}]
        for rr in o.resources:
            x, _ = from_resource(rr)
            r["resources"] += [
                {
                    "resource": rr,
                    "resource__label": str(x),
                    "managed_object": x.managed_object.id,
                    "managed_object__label": str(x.managed_object.name),
                }
            ]
        return r

    @view(url=r"^(?P<sid>[0-9a-f]{24})/caps/$", method=["GET"], access="read", api=True)
    def api_get_caps(self, request, sid):
        o = self.get_object_or_404(Service, id=sid)
        # if not o.has_access(request.user):
        #    return self.response_forbidden("Access denied")
        caps = {}
        for c in o.caps:
            caps[str(c.capability.id)] = {
                "capability": c.capability.name,
                "id": str(c.capability.id),
                "object": str(o.id),
                "description": c.capability.description,
                "type": c.capability.type.value,
                "value": c.value,
                "source": c.source,
                "scope": c.scope or "",
                "editor": c.capability.get_editor() if c.capability.allow_manual else None,
            }
        r = []
        for cp in o.profile.caps:
            cid = str(cp.capability.id)
            if cid in caps:
                c = caps.pop(cid)
                if not cp.allow_manual:
                    c["editor"] = None
                c["value"] = c["value"] or cp.default_value
            else:
                c = {
                    "capability": cp.capability.name,
                    "id": str(cp.capability.id),
                    "object": str(o.id),
                    "description": cp.capability.description,
                    "type": cp.capability.type.value,
                    "value": cp.default_value,
                    "source": "P",
                    "scope": "",
                    "editor": cp.capability.get_editor() if cp.allow_manual else None,
                }
            r.append(c)
        return sorted(r, key=lambda x: x["capability"])

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

    @view("^(?P<sid>[0-9a-f]{24})/instance/$", access="read", api=True)
    def api_get_instance(self, request, sid: str):
        o = self.get_object_or_404(Service, id=sid)
        r = []
        for si in ServiceInstance.objects.filter(service=o):
            r.append(self.instance_to_dict_si(si))
        return r

    @view(
        "^(?P<sid>[0-9a-f]{24})/instance/(?P<iid>[0-9a-f]{24})/$",
        method=["PUT"],
        access="update",
        validate={
            "name": UnicodeParameter(required=False),
            "fqdn": UnicodeParameter(required=False),
            "port": IntParameter(required=False, min_value=0, max_value=65536),
        },
        api=True,
    )
    def api_update_instance(
        self,
        request,
        sid: str,
        iid: str,
        name: Optional[str] = None,
        fqdn: Optional[str] = None,
        port: Optional[int] = None,
    ):
        si = self.get_object_or_404(ServiceInstance, id=iid)
        if si.name != name:
            si.name = name
        if si.fqdn != fqdn:
            si.fqdn = fqdn
        if si.port != port:
            si.port = port
        si.save()
        return {"success": True, "data": self.instance_to_dict_si(si)}

    # New Instance working
    @view(
        r"^(?P<sid>[0-9a-f]{24})/register_instance/(?P<i_type>\S+)/$",
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
            return {"success": True, "message": f"Not supported type: {i_type}"}
        si = o.register_instance(i_type, name=name, fqdn=fqdn)
        return {"success": True, "data": self.instance_to_dict_si(si)}

    @view(
        r"^(?P<sid>[0-9a-f]{24})/unregister_instance/(?P<iid>[0-9a-f]{24})/$",
        method=["POST"],
        access="unregister_instance",
        api=True,
    )
    def api_unregister_instance(
        self,
        request,
        sid: str,
        iid: str,
    ):
        o = self.get_object_or_404(Service, id=sid)
        si = self.get_object_or_404(ServiceInstance, id=iid)
        o.deregister_instance(si.type, name=si.name)
        return {"success": True}

    # Resource Working
    @view(
        r"^(?P<sid>[0-9a-f]{24})/instance/(?P<iid>[0-9a-f]{24})/bind/$",
        method=["PUT"],
        access="update",
        validate=DictParameter(
            attrs={
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
        ),
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
            si.save()
        if managed_object:
            si.refresh_managed_object(managed_object, source=InputSource.MANUAL)
        if resources:
            r = []
            for x in resources:
                x, _ = from_resource(x)
                r.append(x)
            si.update_resources(r, source=InputSource.MANUAL)
        return {"success": True, "data": self.instance_to_dict_si(si)}

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
            si.reset_object()
        elif r_type == "addresses":
            si.deregister_endpoint(InputSource.MANUAL)
            si.save()
        elif r_type == "resources":
            si.update_resources([], InputSource.MANUAL)
        return {"success": True, "data": self.instance_to_dict_si(si)}
