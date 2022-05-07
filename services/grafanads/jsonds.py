# ----------------------------------------------------------------------
# GrafanaDS API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import operator
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Iterable, Union, Set, Any
from collections import defaultdict

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
        SELECT %s as t,
            %s as target,
            %s
        FROM
            %s
        WHERE
            %s
        GROUP BY %s, t ORDER BY t ASC
    )
    GROUP BY target FORMAT JSON
"""

router = APIRouter()


@dataclass
class QueryConfig(object):
    metric_type: str
    query_expression: str
    alias: Optional[str] = None
    aggregate_function: str = "avg"
    if_combinator_condition: str = ""
    description: str = ""


class JsonDSAPI(object):
    """
    Backend for SimpodJson Grafana plugin
    """

    QUERY_CONFIGS: List["QueryConfig"] = None
    openapi_tags = ["api", "grafanads"]
    api_name: str = None
    query_response_model = List[TargetResponseItem]
    variable_payload = None
    allow_interval_limit: bool = True

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.router = router
        self.query_config: Dict[str, "QueryConfig"] = self.load_query_config()
        self.setup_routes()

    @classmethod
    def load_query_config(cls):
        """
        Load Additional QueryConfig on API
        :return:
        """
        r = {}
        for qc in cls.QUERY_CONFIGS or []:
            r[qc.alias or qc.metric_type] = qc
        return r

    async def api_grafanads_search(
        self, req: Dict[str, str], user: User = Depends(get_current_user)
    ):
        """
        Method for /search endpoint on datasource
        :param req:
        :param user:
        :return:
        """
        self.logger.info("Search Request: %s", req)
        return self.get_metrics()

    async def api_grafanads_variable(
        self, req: VariableRequest, user: User = Depends(get_current_user)
    ):
        """
        Method for /variable endpoint on datasource
        :param req:
        :param user:
        :return:
        """
        self.logger.info("Variable Request: %s", req)
        if not self.variable_payload:
            return []
        payload = parse_obj_as(self.variable_payload, req.payload)
        h = getattr(payload, "get_variables", None)
        if not h:
            return []
        return h(user)

    async def api_grafanads_annotations(
        self, req: AnnotationRequest, user: User = Depends(get_current_user)
    ):
        """
        Method for /annotations endpoint on datasource
        :param req:
        :param user:
        :return:
        """
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

    @classmethod
    def get_metrics(cls) -> List[Dict[str, str]]:
        """
        Return Available Metrics for datasource
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
        # Append Query Configs
        for qc in cls.QUERY_CONFIGS or []:
            if qc.alias:
                r += [{"text": qc.description or qc.alias, "value": qc.alias}]
        return r

    @staticmethod
    def clean_func_expr(field_name, function: Optional[str] = None) -> str:
        """
        Return function expression for field
        :param field_name:
        :param function:
        :return:
        """
        if not function:
            return field_name
        if function.lower() in {"argmax", "argmin"}:
            return f"{function}({field_name}, t)"
        return f"{function}({field_name})"

    async def api_grafanads_query(self, req: QueryRequest, user: User = Depends(get_current_user)):
        """
        Method for /query endpoint on datasource

        :param req:
        :param user:
        :return:
        """
        self.logger.info("Query Request: %s", req)
        connect = connection()
        r = []
        targets: Dict[Tuple[str, str], List["QueryConfig"]] = defaultdict(list)
        # Merge targets to Metric Scope and Filter
        for target in req.targets:
            if target.target in self.query_config:
                query_config = self.query_config[target.target]
                metric_type = MetricType.get_by_name(query_config.metric_type)
            else:
                metric_type = MetricType.get_by_id(target.target)
                query_config = QueryConfig(
                    metric_type=metric_type.name, query_expression=metric_type.field_name
                )
            if not metric_type:
                self.logger.error("[%s] Unknown MetricType: %s", target.target, query_config)
                raise HTTPException(status_code=500, detail="Unknown MetricType in QueryConfig")
            # Target Filter
            # {"managed_object": "3780187837837487731"}
            query_mt_condition = self.get_query_metric_type_condition(
                target.payload, metric_type, user=user
            )
            if target.payload and "metric_function" in target.payload:
                # Alternative - target with function suffix, percentile ?
                query_config.aggregate_function = target.payload["agg_func"]
            targets[(metric_type.scope.table_name, query_mt_condition)] += [query_config]
        # Query
        for (table_name, query_condition), query_configs in targets.items():
            # Format query
            query = self.get_query(req, table_name, query_condition, query_configs)
            self.logger.info("Do query: %s", query)
            try:
                result = connect.execute(query, return_raw=True)
            except ClickhouseError as e:
                self.logger.error("Clickhouse query error: %s", e)
                raise HTTPException(status_code=500, detail=e)
            r += self.format_result(
                orjson.loads(result),
                result_type=req.result_type,
                request_metrics={qc.alias or qc.metric_type for qc in query_configs},
            )
        return r

    def get_query(
        self,
        req: QueryRequest,
        table_name: str,
        query_condition: str,
        query_configs: List["QueryConfig"],
    ) -> str:
        """
        Return Query Expression for Clickhouse

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
            GROUP BY target, t ORDER BY t ASC
        )
        GROUP BY target FORMAT JSON

        :param req:
        :param table_name:
        :param query_condition:
        :param query_configs:
        :return:
        """
        # TS Filter
        timestamp_condition: str = self.get_ts_condition(req)
        s_fields = []
        for qc in query_configs:
            if qc.if_combinator_condition:
                # groupArrayIf((t, li), traffic_class = '') AS lii,
                s_fields += [
                    f"groupArrayIf((`{qc.metric_type}`, t), {qc.if_combinator_condition}) AS `{qc.alias or qc.metric_type}`"
                ]
            else:
                s_fields += [
                    f"groupArray((`{qc.metric_type}`, t)) AS `{qc.alias or qc.metric_type}`"
                ]
        target_expr, group_by_expr = self.get_target_expression(table_name)
        timestamp_expr = "(intDiv(toUInt32(ts), 100) * 100) * 1000"
        if self.allow_interval_limit and req.interval.endswith("m"):
            timestamp_expr = f"(intDiv(toUInt32(toStartOfInterval(ts, toIntervalMinute({req.interval[:-1]}))), 100) * 100) * 1000"
        return SQL % (
            ", ".join(s_fields),
            timestamp_expr,
            target_expr,
            ", ".join(
                f"{self.clean_func_expr(qc.query_expression, qc.aggregate_function)} AS `{qc.metric_type}`"
                for qc in query_configs
            ),
            table_name,
            timestamp_condition + (f" AND {query_condition}" if query_condition else ""),
            group_by_expr,
        )

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
    def get_target_expression(table_name: str = None) -> Tuple[str, Optional[str]]:
        """
        Getting Target name format for table
        :param table_name:
        :return:
        """
        return "arrayStringConcat(labels,'/')", "target"

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
    def get_ts_condition(cls, req: QueryRequest) -> str:
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

    def get_query_metric_type_condition(
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
            if isinstance(values, (int, str)):
                values = [str(values)]
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
            response_model=self.query_response_model,
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
