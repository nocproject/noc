# ----------------------------------------------------------------------
# objectmetrics API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from datetime import datetime
import operator
from typing import List, Optional, Any

# Third-party modules
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

# NOC modules
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.pm.models.metrictype import MetricType
from noc.core.clickhouse.connect import ClickhouseClient
from noc.core.clickhouse.error import ClickhouseError
from noc.sa.models.profile import Profile
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

S_INTERFACE = "interface"

router = APIRouter()


class Metrics(BaseModel):
    object: str
    interfaces: Optional[List[str]] = None
    metric_types: List[str]


class ObjectMetricsRequest(BaseModel):
    from_: datetime = Field(..., alias="from")
    to: datetime
    metrics: List[Metrics]


class ObjectMetricsResponseItem(BaseModel):
    object: str
    metric_type: str
    path: List[str]
    values: List[List[Any]]
    interface: Optional[str]


class ObjectMetricsResponse(BaseModel):
    from_: datetime = Field(..., alias="from")
    to: datetime
    metrics: List[ObjectMetricsResponseItem]


class ObjectMetricsAPI(NBIAPI):
    api_name = "objectmetrics"
    openapi_tags = ["objectmetrics API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/objectmetrics",
            "method": "POST",
            "endpoint": self.handler,
            "response_model": ObjectMetricsResponse,
            "name": "objectmetrics",
            "description": "Allows to request specified metrics for particular managed objects",
        }
        return [route]

    async def handler(
        self, req: ObjectMetricsRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)
    ):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        # Check timestamps
        from_ts = req.from_
        to_ts = req.to
        if to_ts < from_ts:
            raise HTTPException(400, "Invalid range")
        # Check time range
        delta = to_ts - from_ts
        if delta.total_seconds() > config.nbi.objectmetrics_max_interval:
            raise HTTPException(400, "Requested range too large")
        # Prepare data for queries
        objects = set()
        for mc in req.metrics:
            try:
                mo_id = int(mc.object)
                objects.add(mo_id)
            except ValueError:
                raise HTTPException(400, f"Invalid object id: {mc.object}")
        #
        if not objects:
            return []
        # Map managed object id to bi_id
        id_to_bi = {}
        profiles = {}  # object id -> profile
        for mo_id, bi_id, profile_id in ManagedObject.objects.filter(
            id__in=list(objects)
        ).values_list("id", "bi_id", "profile"):
            id_to_bi[str(mo_id)] = bi_id
            profiles[str(mo_id)] = Profile.get_by_id(profile_id).get_profile()
        if not id_to_bi:
            raise HTTPException(
                404, f"Object(s) id not found: {','.join([str(o) for o in objects])}"
            )
        # Prepare queries
        scopes = {}  # table_name -> ([fields, ..], [where, ..])
        for mc in req.metrics:
            profile = profiles[mc.object]
            try:
                ifaces = tuple(
                    sorted(profile.convert_interface_name(i) for i in getattr(mc, "interfaces", []))
                )
            except ValueError:
                raise HTTPException(
                    400,
                    f'Invalid interface name: {",".join(getattr(mc, "interfaces", []))} '
                    f"for device: {mc.object}",
                )
            for mn in mc.metric_types:
                mt = MetricType.get_by_name(mn)
                if not mt:
                    raise HTTPException(400, f"Invalid metric_type: {mn}")
                table = mt.scope.table_name
                q = scopes.get(table)
                if not q:
                    q = (set(), set())
                    scopes[table] = q
                q[0].add(mt.field_name)
                if table == S_INTERFACE:
                    q[1].add((id_to_bi[mc.object], ifaces))
                else:
                    q[1].add((id_to_bi[mc.object],))
        # Execute queries and collect result
        from_date = from_ts.strftime("%Y-%m-%d")
        to_date = to_ts.strftime("%Y-%m-%d")
        if from_date == to_date:
            date_q = "date = '%s'" % from_date
        else:
            date_q = "date >= '%s' AND date <= '%s'" % (from_date, to_date)
        date_q = "%s AND ts >= '%s' AND ts <= '%s'" % (
            date_q,
            from_ts.replace(tzinfo=None).isoformat(),
            to_ts.replace(tzinfo=None).isoformat(),
        )
        connect = ClickhouseClient()
        scope_data = {}
        for table in scopes:
            sdata = {}  # managed_object.bi_id, interface, field -> ([(ts, value), ...], path)
            scope_data[table] = sdata
            # Build SQL request
            qx = []
            for wx in scopes[table][1]:
                if len(wx) == 1 or not wx[1]:
                    qx += ["(managed_object = %d)" % wx[0]]
                elif len(wx[1]) == 1:
                    qx += ["(managed_object = %d AND path[4] = '%s')" % (wx[0], wx[1][0])]
                else:
                    qx += [
                        "(managed_object = %d AND path[4] IN (%s))"
                        % (wx[0], ", ".join("'%s'" % x for x in wx[1]))
                    ]
            fields = ["ts", "managed_object", "path"] + sorted(scopes[table][0])
            query = "SELECT %s FROM %s WHERE %s AND (%s)" % (
                ", ".join(fields),
                table,
                date_q,
                " OR ".join(qx),
            )
            # Execute
            self.logger.info("%s", query)
            try:
                data = connect.execute(query)
            except ClickhouseError as e:
                self.logger.error(f"SQL Error: {e}")
                raise HTTPException(500, f"SQL Error: {e}")
            # Process result
            for row in data:
                d = dict(zip(fields, row))
                ts = d.pop("ts")
                mo = int(d.pop("managed_object"))
                path = self.clear_path(d.pop("path"))
                if table == S_INTERFACE:
                    iface = path[3]
                else:
                    iface = None
                for field in d:
                    key = (mo, iface, field)
                    item = (ts, d[field])
                    bucket = sdata.get(key)
                    if bucket:
                        xdata = bucket[0]
                        xdata += [item]
                    else:
                        sdata[key] = ([item], path)
        # Format result
        result = []
        for mc in req.metrics:
            ifaces = tuple(sorted(getattr(mc, "interfaces", [])))
            mo_bi_id = id_to_bi[mc.object]
            for mn in mc.metric_types:
                mt = MetricType.get_by_name(mn)
                table = mt.scope.table_name
                field = mt.field_name
                if table == S_INTERFACE:
                    if_list = ifaces
                else:
                    if_list = (None,)
                sdata = scope_data[table]
                for iface in if_list:
                    key = (mo_bi_id, iface, field)
                    mdata = sdata.get(key)
                    if not mdata:
                        continue
                    points, path = mdata
                    # Clean data type
                    points = sorted(
                        ((p[0].replace(" ", "T"), mt.clean_value(p[1])) for p in points if p[1] != '\\N'),
                        key=operator.itemgetter(0),
                    )
                    #
                    r = {"object": mc.object, "metric_type": mn, "path": path, "values": points}
                    if iface is not None:
                        r["interface"] = iface
                    result += [r]
        # Return response
        return {"from": req.from_, "to": req.to, "metrics": result}

    @staticmethod
    def clear_path(path):
        def q(item):
            if len(item) >= 2 and item[0] == item[-1] and item[0] in ("'", '"'):
                item = item[1:-1]
            return item

        if not path:
            return tuple()
        if len(path) >= 2 and path[0] == "[" and path[-1] == "]":
            path = path[1:-1]
        return tuple(q(x) for x in path.split(","))


# Install router
ObjectMetricsAPI(router)
