# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
from io import BytesIO
from collections import defaultdict
from typing import Dict, Any, Optional, List, Tuple

# Third-party modules
import orjson
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
from noc.main.reportsources.loader import loader as r_source_loader
from noc.core.debug import error_report
from noc.core.middleware.tls import get_user
from noc.core.datasources.base import BaseDataSource
from .types import (
    Template,
    OutputType,
    RunParams,
    ReportConfig,
    ReportBand,
    ReportQuery,
    OutputDocument,
    ROOT_BAND,
)
from .report import Band, DataSet


logger = logging.getLogger(__name__)


class ReportEngine(object):
    """
    Reporting Engine implementation. Report Pipeline:
    RunParams -> ReportEngine -> load_data -> Band -> Formatter -> DocumentFile
    """

    def __init__(self, report_execution_history: bool = False, report_print_error: bool = False):
        self.logger = logger
        self.report_execution_history = report_execution_history
        self.report_print_error = report_print_error

    def run_report(self, r_params: RunParams, user: Optional[Any] = None):
        """
        Run report withs params
        :param r_params: Report params
        :param user: Execute from user
        :return:
        """
        # Handler param
        out: BytesIO = BytesIO()
        report = r_params.report
        template = r_params.get_template()
        out_type = r_params.output_type or template.output_type
        user = user or get_user()
        cleaned_param = self.clean_param(report, r_params.get_params())
        if user:
            cleaned_param["user"] = user
        error, start = None, datetime.datetime.now()
        self.logger.info("[%s] Running report with parameter: %s", report.name, cleaned_param)
        try:
            band = self.load_bands(report, cleaned_param, template)
            self.generate_report(report, template, out_type, out, cleaned_param, band)
        except Exception as e:
            error = str(e)
            if self.report_print_error:
                error_report(logger=self.logger, suppress_log=True)
        if self.report_execution_history:
            self.register_execute(
                report,
                start,
                r_params.get_params(),
                successfully=not error,
                error_text=error,
                user=str(user),
            )
        if error:
            self.logger.error(
                "[%s] Finished report with error: %s ; Params:%s", report.name, error, cleaned_param
            )
            raise ValueError(error)
        self.logger.info("[%s] Finished report with parameter: %s", report.name, cleaned_param)
        output_name = self.resolve_output_filename(run_params=r_params, root_band=band)
        return OutputDocument(
            content=out.getvalue(), document_name=output_name, output_type=out_type
        )

    @classmethod
    def register_execute(
        cls,
        report: ReportConfig,
        start: datetime.datetime,
        params: Dict[str, Any],
        end: Optional[datetime.datetime] = None,
        successfully: bool = False,
        canceled: bool = False,
        error_text: Optional[str] = None,
        user: Optional[str] = None,
    ):
        """
        :param report:
        :param start:
        :param end:
        :param params:
        :param successfully:
        :param canceled:
        :param error_text:
        :param user:
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
                    "report": report.name,
                    "name": report.name,
                    "code": "",
                    "user": str(user),
                    "successfully": successfully,
                    "canceled": canceled,
                    "params": orjson.dumps(params).decode("utf-8"),
                    "error": error_text or "",
                }
            ],
        )

    def generate_report(
        self,
        report: ReportConfig,
        template: Template,
        output_type: OutputType,
        output_stream: bytes,
        params: Dict[str, Any],
        band: Band,
    ):
        """
        Render document
        :return:
        """
        #
        from noc.core.reporter.formatter.loader import loader as df_loader

        formatter = df_loader[template.formatter]
        fmt = formatter(band, template, output_type, output_stream)
        fmt.render_document()

    def clean_param(self, report: ReportConfig, params: Dict[str, Any]):
        """
        Clean and validata input params
        :param report:
        :param params:
        :return:
        """
        # clean_params = params.copy()
        clean_params = {}
        for p in report.parameters or []:
            name = p.name
            value = params.get(name)
            if not value and p.required:
                raise ValueError(f"Required parameter {name} not found")
            elif not value:
                continue
            clean_params[name] = p.clean_value(value)
        return clean_params

    def get_fields(self, band: ReportBand, template: Template) -> List[str]:
        """Return fields list for query"""
        logger.info("[%s] Request datasource fields for band", band.name)
        if not template.bands_format:
            return []
        r = set()
        for name, bf in template.bands_format.items():
            if not bf.columns or name == "header":
                continue
            r |= set(c.name for c in bf.columns)
        return list(r)

    def load_bands(
        self, report: ReportConfig, params: Dict[str, Any], template: Optional[Template] = None
    ) -> Band:
        """
        Generate Report Bands from Config
        Attrs:
            report: Report configuration
            params: Running params
        """
        r = report.get_root_band()
        root = Band.from_report(r, params)
        # Create Root BandData
        if r.source:
            s = r_source_loader[r.source]()
            template.bands_format = s.get_formats()
            root.add_children(s.get_data(**params))
            return root
        deferred = []
        for b in report.bands:
            if b.conditions and not b.is_match(params):
                continue
            if b.name == ROOT_BAND:
                band = root
            else:
                band = Band.from_report(b)
            fields = params.pop("fields", None) or self.get_fields(b, template)
            for num, d in enumerate(self.get_dataset(b.queries, params, fields)):
                band.add_dataset(d, name=b.name if not num else None)
            if band.name == ROOT_BAND:
                continue
            elif b.parent == ROOT_BAND or not b.parent:
                root.add_child(band)
                continue
            r = root.find_band_recursively(b.parent)
            if not r:
                print(f"Unknown parent '{b.parent}'")
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
    def get_dataset(
        cls, queries: List[ReportQuery], ctx: Dict[str, Any], fields: List[str]
    ) -> List[DataSet]:
        """
        Attrs:
            queries: Configuration dataset
            ctx: Report params
        """
        r = []
        if not queries:
            return []
        fields_map = defaultdict(list)
        for f in fields:
            f, *ds = f.split(".")
            if not ds:
                fields_map["*"].append(f)
            elif ds and ds[0] == "all":
                fields_map[f] = []
            elif ds and ds[0] != "all":
                fields_map[f].append(ds[0])
        for num, query in enumerate(queries):
            data, ds_f = None, []
            q_ctx = ctx.copy()
            if not num and "*" in fields_map:
                ds_f = fields_map["*"]
            elif query.datasource and query.datasource in fields_map:
                ds_f = fields_map[query.datasource]
            if query.params:
                q_ctx.update(query.params)
            if query.json_data:
                data = pl.DataFrame(orjson.loads(query.json_data))
            elif num and query.datasource and fields_map and query.datasource not in fields_map:
                continue
            elif query.datasource:
                fields = fields_map[query.datasource] if query.datasource in fields_map else fields
                logger.info("[%s] Query DataSource with fields: %s", query.datasource, ds_f)
                data, key_field = cls.query_datasource(query, q_ctx, fields=ds_f)
            r.append(
                DataSet(name=query.name, data=data, query=query.query, transpose=query.transpose)
            )
        return r

    @classmethod
    def query_datasource(
        cls,
        query: ReportQuery,
        ctx: Dict[str, Any],
        joined_field: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> Tuple[Optional[pl.DataFrame], str]:
        """
        Resolve Datasource for Query
        Attrs:
            query:
            ctx:
            fields:
        """
        from noc.core.datasources.loader import loader as ds_loader

        ds: "BaseDataSource" = ds_loader[query.datasource]
        if not ds:
            raise ValueError(f"Unknown DataSource: {query.datasource}")
        if joined_field and not ds.has_field(joined_field):
            # Joined is not supported
            logger.warning("[%s] Joined field '%s' not available", ds.name, joined_field)
            return None, ""
        elif joined_field and ctx.get("fields"):
            ctx["fields"] += [joined_field]
            # Check not row_index
        elif not joined_field and ctx.get("fields"):
            ctx["fields"] += [ds.row_index]
        row = ds.query_sync(fields=fields, **ctx)
        return row, ds.row_index

    def resolve_output_filename(self, run_params: RunParams, root_band: Band) -> str:
        """
        Return document filename by
        :return:
        """
        template = run_params.get_template()
        output_name = template.get_document_name()
        out_type = run_params.output_type or template.output_type
        ctx = root_band.get_data()
        extension = out_type.value
        if out_type == OutputType.CSV_ZIP:
            extension = OutputType.CSV.value
        return f"{Jinja2Template(output_name).render(ctx) or 'report'}.{extension}"
