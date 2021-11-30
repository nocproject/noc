# ----------------------------------------------------------------------
# grafanads API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from time import mktime

# Third-party modules
import dateutil.parser
from dateutil import tz
from fastapi import APIRouter
from pydantic import BaseModel, Field

# NOC modules
from noc.core.service.loader import get_service
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmclass import AlarmClass


class RangeSingle(BaseModel):
    from_: str = Field(..., alias='from')
    to: str


class RangeSection(BaseModel):
    from_: str = Field(..., alias='from')
    to: str
    raw: RangeSingle


class AnnotationSection(BaseModel):
    name: str
    datasource: str
    enable: bool
    icon_color: str = Field(..., alias='iconColor')
    query: str


class Annotation(BaseModel):
    range: RangeSection
    annotation: AnnotationSection
    rangeRaw: RangeSingle = Field(..., alias='rangeRaw')


router = APIRouter()


@router.post("/api/grafanads/annotations/")
@router.post("/api/grafanads/annotations")
async def api_grafanads_annotations(req: Annotation):
    service = get_service()
    f = dateutil.parser.parse(req.range.from_, ignoretz=False)
    t = dateutil.parser.parse(req.range.to, ignoretz=False)
    if f > t:
        t, f = f, t
    # Convert from UTC
    t = t.astimezone(tz.tzlocal())
    f = f.astimezone(tz.tzlocal())
    t = t.replace(tzinfo=None)
    f = f.replace(tzinfo=None)
    # Annotation to return in reply
    ra = req.annotation
    #
    result = await service.run_in_executor("db", get_annotations, f, t, ra)
    return result


@router.get("/api/grafanads/")
def api_grafanads():
    return "OK"


def get_annotations(f, t, annotation):
    # @todo: Check object is exists
    # @todo: Check access
    mo = ManagedObject.get_by_id(int(annotation.query))
    r = []
    # Get alarms
    r += get_alarms(mo, f, t, annotation)
    r = sorted(r, key=operator.itemgetter("time"))
    return r


def get_alarms(mo, f, t, annotation):
    r = []
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
                r += [
                    {
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000
                        + d["timestamp"].microsecond / 1000,
                        "title": AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }
                ]
            if "clear_timestamp" in d and f <= d["clear_timestamp"] <= t:
                r += [
                    {
                        "annotation": annotation,
                        "time": mktime(d["timestamp"].timetuple()) * 1000
                        + d["timestamp"].microsecond / 1000,
                        "title": "[CLEAR] %s" % AlarmClass.get_by_id(d["alarm_class"]).name
                        # "tags": X,
                        # "text": X
                    }
                ]
    return r
