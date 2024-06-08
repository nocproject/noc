# ----------------------------------------------------------------------
# GrafanaDS API ManagedObject endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Any, Dict
from time import mktime

# Third-party modules
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

# NOC modules
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.interface import Interface
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.models import get_model
from ..models.jsonds import AnnotationSection
from ..models.managedobject import VariablePayloadItem, QueryPayloadItem
from ..jsonds import JsonDSAPI


router = APIRouter()


class ManagedObjectJsonDS(JsonDSAPI):
    api_name = "managedobject"
    query_payload = QueryPayloadItem
    variable_payload = VariablePayloadItem

    def resolve_payload_options(
        self,
        metric,
        name,
        user,
        payload: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """ """
        if name == "metric":
            return super().get_metrics()
        elif name == "managed_object":
            return [
                {"label": mo[0], "value": mo[1]}
                for mo in ManagedObject.objects.filter(is_managed=True)
                .values_list("name", "bi_id")
                .order_by("id")[:10000]
            ]
        elif name == "interface":
            mo = ManagedObject.get_by_bi_id(int(payload["managed_object"]))
            return [
                {"label": iface.name, "value": iface.name}
                for iface in Interface.objects.filter(managed_object=mo, type="physical")
            ]
        return []

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

    @staticmethod
    def iter_alarms_annotations(
        annotation: AnnotationSection,
        f: datetime.datetime,
        t: datetime.datetime,
        user: User = None,
    ):
        mo: "ManagedObject" = ManagedObject.get_by_id(int(annotation.query))
        if not mo:
            raise HTTPException(status_code=404, detail="Managed Object Does Not Exists")
        if not user.is_superuser and mo.administrative_domain.id not in set(
            UserAccess.get_domains(user)
        ):
            raise HTTPException(status_code=404, detail="ManagedObject not Permission")
        for ac in (ActiveAlarm, ArchivedAlarm):
            q = {"managed_object": mo.id}
            if ac.status == "A":
                q["timestamp"] = {"$gte": f, "$lte": t}
            else:
                q["$or"] = [
                    {"timestamp": {"$gte": f, "$lte": t}},
                    {"clear_timestamp": {"$gte": f, "$lte": t}},
                ]
            c = ac._get_collection()
            for d in c.find(
                q,
                {
                    "_id": 1,
                    "managed_object": 1,
                    "alarm_class": 1,
                    "timestamp": 1,
                    "clear_timestamp": 1,
                },
            ):
                if f <= d["timestamp"] <= t:
                    yield {
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000
                        + d["timestamp"].microsecond / 1000,
                        "title": AlarmClass.get_by_id(d["alarm_class"]).name,
                        # "tags": X,
                        # "text": X
                    }
                if "clear_timestamp" in d and f <= d["clear_timestamp"] <= t:
                    yield {
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000
                        + d["timestamp"].microsecond / 1000,
                        "title": "[CLEAR] %s" % AlarmClass.get_by_id(d["alarm_class"]).name,
                        # "tags": X,
                        # "text": X
                    }


# Install endpoints
ManagedObjectJsonDS(router)
