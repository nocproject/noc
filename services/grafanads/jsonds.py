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
from pydantic import TypeAdapter

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
    MetricsPayloadRequest,
    MetricsResponseItem,
    MetricPayloadOptionsRequest,
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
    openapi_tags: List[str] = ["api", "grafanads"]
    api_name: Optional[str] = None
    query_response_model = List[TargetResponseItem]
    variable_payload = None
    allow_interval_limit: bool = True

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.router = router
        self.query_config: Dict[str, "QueryConfig"] = self.load_query_config()
        self.type_adapter = TypeAdapter(self.variable_payload)
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
        return self.get_metrics_for_search()

    async def api_grafanads_metrics(
        self, payload: MetricsPayloadRequest, user: User = Depends(get_current_user)
    ):
        """
        Method for /search endpoint on datasource
        :param payload:
        :param user:
        :return:
        """
        self.logger.info("Search Request: %s", payload)
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
        payload = req.payload
        payload = self.type_adapter.validate_python(orjson.loads(payload.target))
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
    ) -> Iterable["Annotation"]: ...

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
                    "label": mt.name,
                    "value": str(mt.id),
                }
            )
        # Append Query Configs
        for qc in cls.QUERY_CONFIGS or []:
            if qc.alias:
                r += [{"label": qc.description or qc.alias, "value": qc.alias}]
        return r

    @classmethod
    def get_metrics_for_search(cls) -> List[Dict[str, str]]:
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
            elif target.payload and "metric" in target.payload:
                metric_type = MetricType.get_by_id(target.payload["metric"])
                query_config = QueryConfig(
                    metric_type=metric_type.name, query_expression=metric_type.field_name
                )
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
            r += [(query_configs, orjson.loads(result))]
        return self.format_result(r, result_type=req.result_type)

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
    def format_time_series(cls, results: List[Tuple[List["QueryConfig"], Dict[str, Any]]]):
        result = []
        for query_configs, data in results:
            request_metrics = {qc.alias or qc.metric_type for qc in query_configs}
            for row in data["data"]:
                for field in row:
                    if field == "target":
                        continue
                    result.append(
                        {"target": f"{field} | {row['target']}", "datapoints": row[field]}
                    )
                    if field in request_metrics:
                        request_metrics.remove(field)
            # Add metrics without data
            for rm_name in request_metrics:
                result.append({"target": f"{rm_name}", "datapoints": []})
        return result

    @classmethod
    def format_result(
        cls,
        results: List[Tuple[List["QueryConfig"], Dict[str, Any]]],
        result_type: str = "time_series",
    ):
        if not hasattr(cls, f"format_{result_type}"):
            raise HTTPException(
                status_code=404, detail=f"Requested format '{result_type}' not supported"
            )
        return getattr(cls, f"format_{result_type}")(results)

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

    def resolve_payload_options(
        self,
        metric,
        name,
        user,
        payload: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """ """
        return []

    async def api_metric_payload_options(
        self,
        req: MetricPayloadOptionsRequest,
        user: User = Depends(get_current_user),
    ):
        """
        Metric Payload Options API
        """
        self.logger.info("Payload Options Request: %s", req)
        return self.resolve_payload_options(req.metric, req.name, user, req.payload)

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
        return model.objects.filter(name__contains=value).first()

    @classmethod
    def get_metric_scope_fields(cls, metric_scope) -> Tuple[Dict[str, str], Set[str], Set[str]]:
        """
        Get Metric Scope Config. Key Field -> Model map, Required Column, Columns
        :param metric_scope: MetricScope Name
        :return:
        """
        key_fields, required_columns, columns = {}, set(), set()
        for kf in metric_scope.key_fields:
            key_fields[kf.field_name] = kf.model
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
        Processed requested Scope key fields
        :param metric_type:
        :param payload:
        :param user:
        :return:
        """
        if not payload:
            return ""
        r = []
        key_fields, required_columns, columns = self.get_metric_scope_fields(metric_type.scope)
        #
        for query_field, values in payload.items():
            query_field, *query_function = query_field.split("__", 1)
            # Labels
            if query_field == "labels":
                labels = [f"'{ll}'" for ll in payload["labels"]]
                r += [f"labels IN ({','.join(labels)})"]
                continue
            if isinstance(values, (int, str)):
                values = [str(values)]
            if query_field in key_fields:
                q_values = []
                for value in values:
                    if not value.isdigit():
                        # Try Resolve object
                        value = self.resolve_object_query(
                            key_fields[query_field], value, query_function=query_function, user=user
                        )
                        if not value:
                            continue
                        value = value.bi_id
                    q_values += [str(value)]
                r += [f'{query_field} IN ({",".join(q_values)})']
                continue
            elif query_field not in columns or not values:
                continue
            values = [f"'{str(vv)}'" for vv in values]
            if not query_function:
                r += [f"{query_field} = {values[0]}"]
            elif query_function[0].upper() in {"IN", "NOT IN"}:
                r += [f"{query_field} {query_function[0]} ({','.join(values)})"]
            elif query_function[0].upper() in {"MATCH", "REGEX"}:
                r += [f"{query_function[0]}({query_field}, {values[0]})"]
            else:
                r += [f"{query_field} {query_function[0]} {values[0]}"]
        if not r:
            raise HTTPException(status_code=400, detail="One of Key field is required on query")
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

    async def api_test(self):
        return "1"

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
            path=f"/api/grafanads/{self.api_name}/metrics",
            endpoint=self.api_grafanads_metrics,
            methods=["POST"],
            response_model=List[MetricsResponseItem],
            tags=self.openapi_tags,
            name=f"{self.api_name}_metrics",
            description="Getting available metrics",
        )
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}/metric-payload-options",
            endpoint=self.api_metric_payload_options,
            methods=["POST"],
            response_model=List[MetricsResponseItem],
            tags=self.openapi_tags,
            name=f"{self.api_name}_metric_payload_options",
            description="Getting payload options",
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
        self.router.add_api_route(
            path=f"/api/grafanads/{self.api_name}",
            endpoint=self.api_test,
            methods=["GET"],
            tags=self.openapi_tags,
            name=f"{self.api_name}_test",
            description="Test DataSource",
        )
