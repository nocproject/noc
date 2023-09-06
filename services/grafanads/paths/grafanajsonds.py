# ----------------------------------------------------------------------
# Grafana JsonDS API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Any, Dict

# Third-party modules
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from django.db import connection as pg_conn

# NOC modules
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.models import get_model
from ..models.managedobject import VariablePayloadItem, QueryPayloadItem
from ..jsonds import JsonDSAPI


router = APIRouter()


class GrafanaJsonDS(JsonDSAPI):
    api_name = "grafanajsonds"
    query_payload = QueryPayloadItem
    variable_payload = VariablePayloadItem
    MAX_OBJECTS = 10_000
    ALLOWED_KEY_FIELDS = ["managed_object", "sla", "agent"]

    @classmethod
    def get_object_count(cls):
        cursor = pg_conn.cursor()
        cursor.execute(
            """
                  SELECT upper(left(name, 1)) as c, count(*)
                  FROM sa_managedobject
                  GROUP BY upper(left(name, 1))
                  ORDER BY upper(left(name, 1))
                """
        )
        r = []
        g_count, g = 0, []
        for group, count in cursor:
            if g and g_count + count > cls.MAX_OBJECTS:
                r += [g or group]
                g_count, g = 0, []
            g += [group]
            g_count += count
        return r

    @classmethod
    def get_metrics(cls):
        """
        Return PM Scope NameSpaces
        """
        r = []
        for scope in MetricScope.objects.filter():
            payloads = [
                {
                    "name": "metric",
                    "label": "Metric",
                    "type": "select",
                    "width": 40,
                    "reload_metric": True,
                }
            ]
            for f in scope.key_fields:
                if f.field_name not in cls.ALLOWED_KEY_FIELDS:
                    continue
                m = get_model(f.model)
                if m.objects.count() > cls.MAX_OBJECTS:
                    payloads += [
                        {
                            "name": f.field_name,
                            "label": f"{f.model} BI ID",
                            "type": "input",
                            "width": 50,
                        }
                    ]
                else:
                    payloads += [
                        {
                            "name": f.field_name,
                            "label": f.model,
                            "type": "select",
                            "width": 50,
                        }
                    ]
                payloads += [
                    {
                        "name": f"{f.field_name}__query",
                        "label": f"{f.model} Query",
                        "type": "input",
                        "width": 50,
                    }
                ]
            for label in scope.labels:
                if not label.is_key_label:
                    continue
                p_type = "input"
                if label.field_name in ["interface", "subinterface"]:
                    p_type = "multi-select"
                payloads += [
                    {
                        "name": label.field_name,
                        "label": label.field_name,
                        "type": p_type,
                        "width": 40,
                        "reload_metric": True,
                    }
                ]

            r += [
                {
                    "value": str(scope.id),
                    "label": f"Namespace {scope.name}",
                    "payloads": payloads,
                }
            ]
        return r

    @staticmethod
    def resolve_managed_object(payload: Dict[str, str]) -> ManagedObject:
        """
        Find ManagedObject by query
        """
        managed_object = None
        if "managed_object" in payload:
            # Resolve by BI ID
            managed_object = ManagedObject.get_by_bi_id(int(payload["managed_object"]))
        elif "managed_object__query" in payload:
            # Resolve by query
            q = ManagedObject.get_search_Q(payload["managed_object__query"])
            managed_object = ManagedObject.objects.filter(q).first()
        elif "managed_object__name" in payload:
            # Resolve by name
            managed_object = ManagedObject.objects.filter(
                name__contains=payload["managed_object__name"]
            ).first()
        if not managed_object:
            raise HTTPException(status_code=404, detail="Not Found Requested Device")
        return managed_object

    def resolve_payload_options(
        self,
        metric,
        name,
        user,
        payload: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """ """
        r = []
        if name == "metric":
            for mt in MetricType.objects.filter(scope=metric):
                r.append(
                    {
                        "label": mt.name,
                        "value": str(mt.id),
                    }
                )
        elif name == "managed_object":
            return [
                {"label": mo[0], "value": mo[1]}
                for mo in ManagedObject.objects.filter(is_managed=True)
                .values_list("name", "bi_id")
                .order_by("name")[: self.MAX_OBJECTS]
            ]
        elif name == "interface":
            mo = self.resolve_managed_object(payload)
            return [
                {"label": iface.name, "value": iface.name}
                for iface in Interface.objects.filter(
                    managed_object=mo, type__in=["aggregated", "physical"]
                ).order_by("name")
            ]
        elif name == "subinterface":
            mo = self.resolve_managed_object(payload)
            return [
                {"label": si.name, "value": si.name}
                for si in SubInterface.objects.filter(managed_object=mo).order_by("name")
            ]
        return r

    @staticmethod
    def resolve_object_query(
        model_id, value, query_function: Optional[List[str]] = None, user: User = None
    ) -> Optional[Any]:
        """
        Resolve object in Query by Value
        :param model_id:
        :param value:
        :param query_function:
        :param user:
        :return:
        """
        model = get_model(model_id)
        obj = model.objects.filter(name__contains=value).first()
        if (
            obj
            and model_id == "sa.ManagedObject"
            and not user.is_superuser
            and obj.administrative_domain.id not in UserAccess.get_domains(user)
        ):
            raise HTTPException(status_code=404, detail="Not Access to requested device")
        return obj


# Install endpoints
GrafanaJsonDS(router)
