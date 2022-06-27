# ----------------------------------------------------------------------
# GrafanaDS API ManagedObject endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional
from time import mktime

# Third-party modules
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

# NOC modules
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
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

    @staticmethod
    def resolve_object_query(model_id, value, user: User = None) -> Optional[int]:
        """
        Resolve object in Query by Value
        :param model_id:
        :param value:
        :param user:
        :return:
        """
        model = get_model(model_id)
        obj = model.objects.filter(name=value).first()
        if (
            obj
            and model_id == "sa.ManagedObject"
            and not user.is_superuser
            and obj.administrative_domain not in UserAccess.get_domains(user)
        ):
            raise HTTPException(status_code=404, detail="Not Access to requested device")
        return obj.bi_id if obj else None

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
                        "title": AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }
                if "clear_timestamp" in d and f <= d["clear_timestamp"] <= t:
                    yield {
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000
                        + d["timestamp"].microsecond / 1000,
                        "title": "[CLEAR] %s" % AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }


# Install endpoints
ManagedObjectJsonDS(router)
