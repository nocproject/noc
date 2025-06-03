# ----------------------------------------------------------------------
# service datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.service import Service
from noc.inv.models.resourcegroup import ResourceGroup
from ..models.service import ServiceDataStreamItem
from noc.core.comp import smart_text
from noc.core.mx import (
    MX_LABELS,
    MX_PROFILE_ID,
    MX_H_VALUE_SPLITTER,
    MX_RESOURCE_GROUPS,
)


def qs(s):
    if not s:
        return ""
    return smart_text(s)


class ServiceDataStream(DataStream):
    name = "service"
    model = ServiceDataStreamItem

    @classmethod
    def get_object(cls, id):
        svc = Service.objects.filter(id=id).first()
        if not svc:
            raise KeyError()
        r = {
            "id": str(svc.id),
            "$version": 1,
            "label": qs(svc.label),
            "bi_id": svc.bi_id,
            cls.F_LABELS_META: svc.effective_labels,
            # cls.F_ADM_DOMAIN_META: svc.administrative_domain.id,
            cls.F_GROUPS_META: [str(rg) for rg in svc.effective_service_groups],
        }
        if svc.description:
            r["description"] = str(svc.description)
        if svc.labels:
            r["labels"] = [qs(x) for x in svc.labels]
        if svc.parent:
            r["parent"] = str(svc.parent.id)
        if svc.agreement_id:
            r["agreement_id"] = svc.agreement_id
        if svc.address:
            r["address"] = svc.address
        cls._apply_state(svc, r)
        cls._apply_caps(svc, r)
        cls._apply_profile(svc, r)
        cls._apply_remote_system(svc, r)
        cls._apply_resource_groups(svc, r)
        return r

    @staticmethod
    def _apply_state(svc, r):
        r["state"] = {
            "id": str(svc.state.id),
            "name": qs(svc.state.name),
            "workflow": {
                "id": str(svc.state.workflow.id),
                "name": qs(svc.state.workflow.name),
            },
        }
        # if address.allocated_till:
        #     r["state"]["allocated_till"] = address.allocated_till.isoformat()

    @staticmethod
    def _apply_caps(svc: Service, r):
        # Get caps
        cdata = svc.get_caps()
        if not cdata:
            return
        caps = []
        for cname in sorted(cdata):
            caps += [{"name": cname, "value": str(cdata[cname])}]
        r["capabilities"] = caps

    @staticmethod
    def _apply_profile(svc, r):
        r["profile"] = {"id": str(svc.profile.id), "name": qs(svc.profile.name)}

    @staticmethod
    def _apply_remote_system(svc, r):
        if svc.remote_system:
            r["remote_system"] = {
                "id": str(svc.remote_system.id),
                "name": qs(svc.remote_system.name),
            }
            r["remote_id"] = svc.remote_id

    @staticmethod
    def _apply_resource_groups(svc: Service, r):
        if svc.effective_service_groups:
            r["service_groups"] = ServiceDataStream._get_resource_groups(
                svc.effective_service_groups, svc.static_service_groups
            )
        if svc.effective_client_groups:
            r["client_groups"] = ServiceDataStream._get_resource_groups(
                svc.effective_client_groups, svc.static_client_groups
            )

    @staticmethod
    def _get_resource_groups(groups, static_groups):
        r = []
        for g in groups:
            rg = ResourceGroup.get_by_id(g)
            if not rg:
                continue
            r += [
                {
                    "id": str(g),
                    "name": qs(rg.name),
                    "technology": qs(rg.technology.name),
                    "static": g in static_groups,
                }
            ]
        return r

    @classmethod
    def get_meta(cls, data):
        return {
            "service_groups": [g["id"] for g in data.get("service_groups", [])],
            "client_groups": [g["id"] for g in data.get("client_groups", [])],
        }

    @classmethod
    def filter_service_group(cls, name: str):
        return {f"{cls.F_META}.service_groups": {"$elemMatch": {"$elemMatch": {"$in": [name]}}}}

    @classmethod
    def filter_client_group(cls, name: str):
        return {f"{cls.F_META}.client_groups": {"$elemMatch": {"$elemMatch": {"$in": [name]}}}}

    @classmethod
    def get_meta_headers(cls, data: Dict[str, Any]) -> Optional[Dict[str, bytes]]:
        if "$deleted" in data:
            # @@todo Meta fields for deleted object
            return
        return {
            # MX_ADMINISTRATIVE_DOMAIN_ID: str(data[cls.F_ADM_DOMAIN_META]).encode(),
            MX_LABELS: str(MX_H_VALUE_SPLITTER.join(data[cls.F_LABELS_META])).encode(),
            MX_PROFILE_ID: str(data["profile"]["id"]).encode(),
            MX_RESOURCE_GROUPS: str(MX_H_VALUE_SPLITTER.join(data[cls.F_GROUPS_META])).encode(),
        }
