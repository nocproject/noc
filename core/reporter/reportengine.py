# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
from io import BytesIO
from collections import defaultdict
from typing import Any

# Third-party modules
import orjson
import polars as pl
from jinja2 import Template as Jinja2Template
from jinja2.exceptions import TemplateError

# NOC modules
from noc.main.reportsources.loader import loader as r_source_loader
from noc.core.debug import error_report
from noc.core.middleware.tls import get_user
from noc.core.datasources.base import BaseDataSource
from noc.core.datasources.loader import loader as ds_loader
from noc.core.reporter.band import Band, DataSet
from noc.core.reporter.formatter.loader import loader as df_loader
from noc.core.reporter.types import (
    Template,
    OutputType,
    RunParams,
    ReportConfig,
    ReportQuery,
    OutputDocument,
    ROOT_BAND,
    HEADER_BAND,
)

logger = logging.getLogger(__name__)


class ReportEngine:
    """
    Reporting Engine implementation. Report Pipeline:
    RunParams -> ReportEngine -> load_data -> Band -> Formatter -> DocumentFile
    """

    def __init__(
        self, report_execution_history: bool = False, report_print_error: bool = False
    ) -> None:
        self.logger = logger
        self.report_execution_history = report_execution_history
        self.report_print_error = report_print_error
        self.suppress_error_log = True

    def run_report(self, r_params: RunParams, user: Any | None = None):
        """
        Run report withs params
        :param r_params: Report params
        :param user: Execute from user
        :return:
        """
        # Handler param
        out: BytesIO = BytesIO()
        rc = r_params.report_config
        template = r_params.get_template()
        out_type = r_params.output_type or template.output_type
        user = user or get_user()
        cleaned_param = self.clean_param(rc, r_params.get_params())
        if user:
            cleaned_param["user"] = user
        selected_fields = cleaned_param.get("fields")
        error, start = None, datetime.datetime.now()
        self.logger.info("[%s] Running report with parameter: %s", rc.name, cleaned_param)
        try:
            band = self.load_bands(rc, cleaned_param, template)
            self.generate_report(template, out_type, out, band, selected_fields)
        except Exception as e:
            error = str(e)
            if self.report_print_error:
                error_report(logger=self.logger, suppress_log=self.suppress_error_log)
        if self.report_execution_history:
            self.register_execute(
                rc,
                start,
                r_params.get_params(),
                successfully=not error,
                error_text=error,
                user=str(user),
            )
        if error:
            self.logger.error(
                "[%s] Finished report with error: %s ; Params:%s", rc.name, error, cleaned_param
            )
            raise ValueError(error)
        self.logger.info("[%s] Finished report with parameter: %s", rc.name, cleaned_param)
        output_name = self.resolve_output_filename(run_params=r_params, root_band=band)
        return OutputDocument(
            content=out.getvalue(), document_name=output_name, output_type=out_type
        )

    @classmethod
    def register_execute(
        cls,
        rc: ReportConfig,
        start: datetime.datetime,
        params: dict[str, Any],
        end: datetime.datetime | None = None,
        successfully: bool = False,
        canceled: bool = False,
        error_text: str | None = None,
        user: str | None = None,
    ):
        """
        :return:
        """
        from noc.core.service.loader import get_service

        svc = get_service()

        end = end or datetime.datetime.now()
        svc.register_metrics(
            "reportexecutionhistory",
            [
                {
                    "date": start.date().isoformat(),
                    "start": start.replace(microsecond=0).isoformat(),
                    "end": end.replace(microsecond=0).isoformat(),
                    "duration": int(abs((end - start).total_seconds()) * 1000),
                    "report": rc.name,
                    "name": rc.name,
                    "code": "",
                    "user": str(user),
                    "successfully": successfully,
                    "canceled": canceled,
                    "params": orjson.dumps(params).decode("utf-8"),
                    "error": error_text or "",
                }
            ],
        )

    @staticmethod
    def generate_report(
        template: Template,
        output_type: OutputType,
        output_stream: bytes,
        band: Band,
        selected_fields: list[str] | None,
    ):
        """Render document"""
        formatter = df_loader[template.formatter]
        fmt = formatter(band, template, output_type, output_stream, selected_fields)
        fmt.render_document()

    @staticmethod
    def align_date(date: datetime.datetime) -> datetime.datetime:
        """Align end date parameter"""
        return (date + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)

    def clean_param(self, rc: ReportConfig, params: dict[str, Any]):
        """Clean and validata input params"""
        # clean_params = params.copy()
        clean_params = {}
        for p in rc.parameters or []:
            name = p.name
            value = params.get(name)
            if not value and p.required:
                raise ValueError(f"Required parameter {name} not found")
            if not value and p.default_value:
                value = p.default_value
            elif not value:
                continue
            clean_params[name] = p.clean_value(value)
            if name == "end" and p.type == "date" and rc.align_end_date_param:
                clean_params[name] = self.align_date(clean_params[name])
        return clean_params

    @staticmethod
    def parse_fields(template: Template, fields: list[str] | None = None) -> dict[str, list[str]]:
        """Parse requested fields for apply to datasource query"""
        logger.info("Request datasource fields for template '%s'", template.code)
        if not template.bands_format and not fields:
            return {}
        if fields:
            fields = set(fields)
        else:
            fields = set()
            for name, bf in template.bands_format.items():
                if not bf.columns or name == HEADER_BAND:
                    continue
                fields |= {c.name for c in bf.columns}
        r = defaultdict(list)
        for f in fields:
            f, *ds = f.split(".")
            if not ds:
                r["*"].append(f)
            elif ds and ds[0] == "all":
                r[f] = []
            elif ds and ds[0] != "all":
                r[f].append(ds[0])
        return r

    def load_bands(self, rc: ReportConfig, params: dict[str, Any], template: Template) -> Band:
        """
        Generate Report Bands from Config
        Attrs:
            rc: Report configuration
            params: Running params
        """
        r = rc.get_root_band()
        root = Band.from_report(r, params)
        # Create Root BandData
        if r.source:
            s = r_source_loader[r.source]()
            template.bands_format = s.get_formats()
            root.add_children(s.get_data(**params))
            return root
        deferred = []
        f_map = self.parse_fields(template, params.pop("fields", None))
        for b in rc.bands:
            if b.conditions and not b.is_match(params):
                continue
            if b.name == ROOT_BAND:
                band = root
            else:
                band = Band.from_report(b)
            for num, d in enumerate(self.get_datasets(b.queries, params, f_map)):
                self.logger.debug(
                    "[%s] Add dataset, Columns [%s]: %s",
                    b.name,
                    d.data.columns if d.data is not None else [],
                    d,
                )
                band.add_dataset(d, name=b.name if not num else None)
            if band.name == ROOT_BAND:
                continue
            if b.parent == ROOT_BAND or not b.parent:
                root.add_child(band)
                continue
            r = root.find_band_recursively(b.parent)
            if not r:
                self.logger.warning(f"Unknown parent '{b.parent}'")
                deferred.append((b.parent, band))
                continue
            r.add_child(band)
        for parent, band in deferred:
            r = root.find_band_recursively(parent)
            if not r:
                raise ValueError("Unknown parent: %s", parent)
            r.add_child(band)
        return root

    @classmethod
    def get_datasets(
        cls, queries: list[ReportQuery], ctx: dict[str, Any], fields_map: dict[str, list[str]]
    ) -> list[DataSet]:
        """
        Attrs:
            queries: Configuration dataset
            ctx: Report params
        """
        result: list[DataSet] = []
        if not queries:
            return []
        joined_fields_map = {}
        for num, query in enumerate(queries):
            data, ds_f = None, []
            q_ctx = ctx.copy()
            if query.datasource and query.datasource in fields_map:
                ds_f = fields_map[query.datasource]
            elif not num and "*" in fields_map:
                ds_f = fields_map["*"]
            if query.params:
                q_ctx.update(query.params)
            if query.json_data:
                data = pl.DataFrame(orjson.loads(query.json_data))
            elif num and query.datasource and fields_map and query.datasource not in fields_map:
                continue
            elif query.datasource:
                logger.info("[%s] Query DataSource with fields: %s", query.datasource, ds_f)
                data, key_fields = cls.query_datasource(query, q_ctx, fields=ds_f)
                joined_fields_map[query.name] = key_fields
            if num and query.name in joined_fields_map:
                jf = set(joined_fields_map[query.name]).intersection(
                    joined_fields_map[result[-1].name]
                )
                result[-1].data = result[-1].data.join(data, on=list(jf), how="left")
            else:
                result.append(
                    DataSet(
                        name=query.name,
                        data=data,
                        query=query.query,
                        transpose=query.transpose,
                        transpose_columns=query.transpose_columns,
                    )
                )
        return result

    @classmethod
    def query_datasource(
        cls, query: ReportQuery, ctx: dict[str, Any], fields: list[str] | None = None
    ) -> tuple[pl.DataFrame | None, list[str]]:
        """
        Resolve Datasource for Query
        Attrs:
            query:
            ctx:
            fields:
        """
        ds: BaseDataSource = ds_loader[query.datasource]
        if not ds:
            raise ValueError(f"Unknown DataSource: {query.datasource}")
        if fields:
            fields += ds.join_fields()
        row = ds.query_sync(fields=fields, **ctx)
        return row, ds.join_fields()

    def resolve_output_filename(self, run_params: RunParams, root_band: Band) -> str:
        """
        Return document filename by
        :return:
        """
        template = run_params.get_template()
        output_name = template.get_document_name()
        out_type = run_params.output_type or template.output_type
        ctx = root_band.get_data()
        ctx["now"] = datetime.datetime.now().replace(microsecond=0)
        extension = out_type.value
        if out_type == OutputType.CSV_ZIP:
            extension = OutputType.CSV.value
        try:
            fn = Jinja2Template(output_name).render(ctx) or "report"
        except TemplateError as e:
            self.logger.error("Error when build filename: %s", str(e))
            fn = "report"
        return f"{fn}.{extension}"
