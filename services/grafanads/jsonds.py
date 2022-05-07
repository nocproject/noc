# ----------------------------------------------------------------------
# GrafanaDS API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, List, Tuple, Optional, Iterable, Union, Set, Any
from collections import defaultdict
import operator

# Third-party modules
import orjson
from dateutil import tz
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import parse_obj_as

# NOC modules
from noc.aaa.models.user import User
from noc.models import get_model
from noc.core.service.deps.user import get_current_user
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.error import ClickhouseError
from noc.core.service.loader import get_service
from noc.pm.models.metrictype import MetricType
from .models.jsonds import (
    QueryRequest,
    TargetResponseItem,
    SearchResponseItem,
    AnnotationRequest,
    AnnotationSection,
    Annotation,
    VariableRequest,
    TagValueQuery,
)

SQL = """
    SELECT
        target,
        %s
    FROM
    (
        SELECT (intDiv(toUInt32(ts), 100) * 100) * 1000 as t,
            %s as target,
            %s
        FROM
            %s
        WHERE
            %s
        GROUP BY labels, t ORDER BY t ASC
    )
    GROUP BY target FORMAT JSON
"""

router = APIRouter()


class JsonDSAPI(object):
    """
    Backend for SimpodJson Grafana plugin
    """

    openapi_tags = ["api", "grafanads"]
    api_name: str = None
    query_payload = None
    variable_payload = None

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.router = router
        self.setup_routes()

    async def api_grafanads_search(
        self, req: Dict[str, str], user: User = Depends(get_current_user)
    ):
        self.logger.info("Search Request: %s", req)
        return self.get_metrics()

    async def api_grafanads_variable(
        self, req: VariableRequest, user: User = Depends(get_current_user)
    ):
        self.logger.info("Variable Request: %s", req)
        if not self.variable_payload:
            return []
        payload = parse_obj_as(self.variable_payload, req.payload)
        h = getattr(self, f"var_{payload.target or 'default'}", None)
        if not h:
            return []
        return h(payload, user)

    async def api_grafanads_annotations(
        self, req: AnnotationRequest, user: User = Depends(get_current_user)
    ):
        self.logger.debug("Annotation Request: %s", req)
        start, end = self.convert_ts_range(req)
        return list(
            sorted(
                self.iter_alarms_annotations(req.annotation, start, end, user),
                key=operator.itemgetter("time"),
            )
        )

    @staticmethod
    def iter_alarms_annotations(
        annotation: AnnotationSection, f: datetime.datetime, t: datetime.datetime, user: User = None
    ) -> Iterable["Annotation"]:
        ...

    @staticmethod
    def get_metrics() -> List[Dict[str, str]]:
        """
        Return Available Metrics
        :return:
        """
        r = []
        for mt in MetricType.objects.filter():
            r.append(
                {
                    "text": mt.name,
                    "value": str(mt.id),
                }
            )
        return r

    @staticmethod
    def clean_query_func(field_name, function) -> Optional[str]:
        if function.lower() in {"argmax", "argmin"}:
            return f"{function}({field_name}, t)"
        return f"{function}({field_name})"

    async def api_grafanads_query(self, req: QueryRequest, user: User = Depends(get_current_user)):
        """
            SELECT
                target,
                %s
            FROM
            (
                SELECT (intDiv(toUInt32(ts), 100) * 100) * 1000 as t,
                    name as target,
                    %s
                FROM
                    %s
                WHERE
                    %s
                GROUP BY name, t ORDER BY t ASC
            )
            GROUP BY name FORMAT JSON

        :param req:
        :param user:
        :return:
        """
        self.logger.info("Query Request: %s", req)
        connect = connection()
        r = []
        # TS Filter
        ts_filter = self.get_ts_filter(req)
        targets: Dict[Tuple[str, str], List[MetricType]] = defaultdict(list)
        # Merge targets to Metric Scope and Filter
        for target in req.targets:
            metric_type = MetricType.get_by_id(target.target)
            # Target Filter
            # {"managed_object": "3780187837837487731"}
            mt_filter = self.get_metric_type_filter(target.payload, metric_type, user=user)
            query_field = f"avg({metric_type.field_name})"
            if target.payload and "metric_function" in target.payload:
                # Alternative - target with function suffix, percentile ?
                query_field = self.clean_query_func(
                    metric_type.field_name, target.payload["agg_func"]
                )
            targets[(metric_type.scope.table_name, mt_filter)] += [(metric_type, query_field)]
        # Query
        for (table_name, mt_filter), metric_types in targets.items():
            # avg(usage) as `CPUUsage`
            query = SQL % (
                ", ".join(f"groupArray((`{mt.name}`, t)) AS `{mt.name}`" for mt, _ in metric_types),
                self.get_target_format(table_name),
                ", ".join(f"{query_field} AS `{mt.name}`" for mt, query_field in metric_types),
                table_name,
                ts_filter + (f" AND {mt_filter}" if mt_filter else ""),
            )
            self.logger.debug("Do query: %s", query)
            try:
                result = connect.execute(query, return_raw=True)
            except ClickhouseError as e:
                self.logger.error("Clickhouse query error: %s", e)
                raise HTTPException(status_code=500, detail=e)
            r += self.format_result(
                orjson.loads(result),
                result_type=req.result_type,
                request_metrics={mt.name for mt, _ in metric_types},
            )
        return r

    @classmethod
    def format_result(
        cls, result, result_type: str = "timeseries", request_metrics: Set["str"] = None
    ):
        """
        Formatting output
        :param result:
        :param result_type:
        :param request_metrics: Set requested metric
        :return:
        """
        r = []
        for row in result["data"]:
            for field in row:
                if field == "target":
                    continue
                r.append({"target": f"{field} | {row['target']}", "datapoints": row[field]})
                if field in request_metrics:
                    request_metrics.remove(field)
        # Add metrics without data
        for rm_name in request_metrics:
            r.append({"target": f"{rm_name}", "datapoints": []})
        return r

    @staticmethod
    def get_target_format(table_name: str = None) -> str:
        """
        Getting Target name format for table
        :param table_name:
        :return:
        """
        return "arrayStringConcat(labels,'/')"

    @staticmethod
    def convert_ts_range(req) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        Convert request range param to local datetime
        :param req:
        :return:
        """
        start, end = req.range.from_, req.range.to
        if start > end:
            end, start = start, end
        # Convert from UTC
        end = end.astimezone(tz.tzlocal())
        start = start.astimezone(tz.tzlocal())
        end = end.replace(microsecond=0, tzinfo=None)
        start = start.replace(microsecond=0, tzinfo=None)
        return start, end

    @classmethod
    def get_ts_filter(cls, req: QueryRequest) -> str:
        """
        Convert Range params to where expression

        date >= toDate(1650542193) AND ts >= toDateTime(1650542193)
        :param req:
        :return:
        """
        start, end = cls.convert_ts_range(req)
        r = [
            f"date >= '{start.date().isoformat()}'",
            f"ts >= '{start.isoformat(sep=' ')}'",
        ]
        if req.range.raw.to != "now":
            r += [
                f"date <= '{end.date().isoformat()}'",
                f"ts <= '{end.isoformat(sep=' ')}'",
            ]
        return " AND ".join(r)

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
        return obj.bi_id if obj else None

    @classmethod
    def get_metric_scope_fields(
        cls, metric_scope
    ) -> Tuple[List[Tuple[str, str]], Set[str], Set[str]]:
        """
        Get Metric Scope Config
        :param metric_scope:
        :return:
        """
        key_fields, required_columns, columns = [], set(), set()
        for kf in metric_scope.key_fields:
            key_fields += [(kf.field_name, kf.model)]
        for lf in metric_scope.labels:
            field = lf.store_column or lf.view_column
            if not field:
                continue
            columns.add(field)
            if lf.is_required:
                required_columns.add(field)
        return key_fields, required_columns, columns

    def get_metric_type_filter(
        self,
        payload: Dict[str, Union[str, List[str]]],
        metric_type: Optional["MetricType"] = None,
        user: User = None,
    ) -> str:
        """
        Convert payload target to where expression
        :param metric_type:
        :param payload:
        :param user:
        :return:
        """
        if not payload:
            return ""
        r = []
        key_fields, required_columns, columns = self.get_metric_scope_fields(metric_type.scope)
        # Labels
        if "labels" in payload:
            labels = [f"'{ll}'" for ll in payload["labels"]]
            r += [f"labels IN ({','.join(labels)})"]
        # Key field
        for kf_name, kf_mode_id in key_fields:
            if kf_name not in payload:
                continue
            values = payload[kf_name]
            if isinstance(values, str):
                values = [values]
            q_values = []
            for value in values:
                if not value.isdigit():
                    # Try Resolve object
                    value = self.resolve_object_query(kf_mode_id, value, user=user)
                    if not value:
                        continue
                q_values += [str(value)]
            r += [f'{kf_name} IN ({",".join(q_values)})']
        if not r:
            raise HTTPException(status_code=400, detail="One of Key field is required on query")
        #
        for query_field, values in payload.items():
            query_field, *query_function = query_field.split("__", 1)
            if query_field not in columns or query_field == "labels":
                continue
            if isinstance(values, str):
                values = [values]
            values = [f"'{str(vv)}'" for vv in values]
            if not query_function:
                r += [f"{query_field} = {values[0]}"]
            elif query_function[0].upper() in {"IN", "NOT IN"}:
                r += [f"{query_field} {query_function[0]} ({','.join(values)})"]
            else:
                r += [f"{query_field} {query_function[0]} {values[0]}"]
        # @todo dict request
        # if lf.is_required and field not in payload:
        #     raise HTTPException(status_code=400, detail=f"Field {field} is required in query")
        #
        # try:
        #     payload = self.query_payload.parse_obj(payload)
        # except ValidationError as e:
        #     raise HTTPException(status_code=400, detail=str(e)) from e
        # return payload.expr
        return " AND ".join(r)

    async def api_grafanads_tag_keys(self, req: Any = None, user: User = Depends(get_current_user)):
        self.logger.info("Tag Key Request: %s", req)
        return self.get_tag_keys()

    def get_tag_keys(self):
        if not self.variable_payload or not hasattr(self.variable_payload, "get_variable_keys"):
            return []
        return self.variable_payload.get_variable_keys()

    async def api_grafanads_tag_values(
        self, req: TagValueQuery, user: User = Depends(get_current_user)
    ):
        self.logger.info("Tag Values Request: %s", req)
        return self.get_tag_values(req.key)

    def get_tag_values(self, key: str):
        """
        Get Values by Requested key
        :param key:
        :return:
        """
        return []

    def setup_routes(self):
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}/search",
            endpoint=self.api_grafanads_search,
            methods=["POST"],
            response_model=List[SearchResponseItem],
            tags=self.openapi_tags,
            name=f"{self.api_name}_search",
            description="Getting available metrics",
        )
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}/query",
            endpoint=self.api_grafanads_query,
            methods=["POST"],
            response_model=List[TargetResponseItem],
            tags=self.openapi_tags,
            name=f"{self.api_name}_query",
            description="Getting target datapoints",
        )
        # Backward compatible
        self.router.add_api_route(
            path="/api/grafanads/annotations",
            endpoint=self.api_grafanads_annotations,
            methods=["POST"],
            response_model=List[Annotation],
            tags=self.openapi_tags,
            name=f"{self.api_name}_annotations_back",
            description="Getting target annotations (Backward compatible)",
        )
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}/annotations",
            endpoint=self.api_grafanads_annotations,
            methods=["POST"],
            response_model=List[Annotation],
            tags=self.openapi_tags,
            name=f"{self.api_name}_annotations",
            description="Getting target annotations",
        )
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}/variable",
            endpoint=self.api_grafanads_variable,
            methods=["POST"],
            response_model=List[Union[Dict[str, str], str]],
            tags=self.openapi_tags,
            name=f"{self.api_name}_variable",
            description="Getting target variable",
        )
