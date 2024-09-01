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
from typing import Dict, Any, Optional, List, Iterable, Tuple, Set

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
    ReportQuery,
    ReportBand,
    OutputDocument,
)
from .report import BandData


logger = logging.getLogger(__name__)


class ReportEngine(object):
    """
    Reporting Engine implementation. Report Pipeline:
    RunParams -> ReportEngine -> load_data -> DataBand -> Formatter -> DocumentFile
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
            data = self.load_data(report, cleaned_param)
            self.generate_report(report, template, out_type, out, cleaned_param, data)
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
        output_name = self.resolve_output_filename(run_params=r_params, root_band=data)
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
        band_data: BandData,
    ):
        """Render document"""
        from noc.core.reporter.formatter.loader import loader as df_loader

        formatter = df_loader[template.formatter]
        fmt = formatter(band_data, template, output_type, output_stream)
        fmt.render_document()

    def clean_param(self, report: ReportConfig, params: Dict[str, Any]):
        """
        Clean and validata input params
        :param report:
        :param params:
        :return:
        """
        # clean_params = params.copy()
        logger.info("Clean params: %s", params)
        clean_params = {}
        for p in report.parameters or []:
            name = p.name
            value = params.get(name)
            if not value and p.required:
                raise ValueError(f"Required parameter {name} not found")
            elif not value:
                continue
            clean_params[name] = p.clean_value(value)
        if report.root_band.queries and "fields" not in params:
            clean_params["fields"] = self.get_root_fields(report, params)
        return clean_params

    def get_root_fields(self, report: "ReportConfig", params) -> List[str]:
        """Build all root fields"""
        t = report.get_template(None)
        r = []
        for b, f in t.bands_format.items():
            if f.header_only:
                continue
            for c in f.columns or []:
                r.append(c.name)
        return r

    def iter_bands_data(
        self, report_band: ReportBand, root_band: BandData, root, params: Dict[str, Any]
    ) -> Iterable[BandData]:
        """
        Attrs:
            report_band:
            root_band:
        """
        if not report_band.is_match(params):
            return
        rows: Optional[pl.DataFrame] = self.get_rows(
            report_band.queries, root_band.get_data(), root_band=root
        )
        if not report_band.has_children:
            band = BandData(
                report_band.name,
                root_band,
                report_band.orientation,
            )
            band.rows = rows
            yield band
            return
        for d in rows.to_dicts():
            band = BandData(
                report_band.name,
                root_band,
                report_band.orientation,
            )
            band.set_data(d)
            yield band

    def load_data(self, report: ReportConfig, params: Dict[str, Any]) -> BandData:
        """
        Generate BandData from ReportBand
        Attrs:
            report:
            params:
        """
        report_band = report.get_root_band()
        # Create Root BandData
        root = BandData(BandData.ROOT_BAND_NAME)
        root.set_data(params)
        if report_band.source:
            # For Source based report
            s = r_source_loader[report_band.source]()
            band = BandData(name="rows")
            band.format = s.get_format()
            band.add_children(s.get_data(**params))
            root.add_child(band)
            return root
        root.rows = self.get_rows(report_band.queries, params)
        # Extract data from ReportBand
        for rb in report_band.iter_nester():
            bd_parent = root.find_band_recursively(rb.parent.name)
            logger.info(
                "Processed ReportBand: %s; Parent BandData: %s", rb.name, bd_parent
            )  # Level needed ?
            if bd_parent.parent:
                # Fill parent DataBand children row
                for c in bd_parent.parent.get_children_by_name(rb.parent.name):
                    for band in self.iter_bands_data(rb, c, root, params):
                        c.add_child(band)
                continue
            for band in self.iter_bands_data(rb, bd_parent, root, params):
                bd_parent.add_child(band)
        return root

    @staticmethod
    def merge_ctx(
        ctx: Dict[str, Any],
        query: ReportQuery,
        joined: bool = False,
    ) -> Tuple[Dict[str, Any], Set[str]]:
        """
        Merge Query context
        Args:
            ctx: Query context (from param)
            query: Query instance
            joined: Joined query flag
        """
        q_ctx = ctx.copy()
        if query.params:
            q_ctx.update(query.params)
        q_ctx["fields"], dss = [], set()
        for f in ctx.get("fields", []):
            ff, *field = f.split(".", 1)
            if not field and not joined:
                # Base datasource
                q_ctx["fields"].append(ff)
            elif field and ff == query.datasource and field[0] != "all":
                q_ctx["fields"] += field
            if field:
                dss.add(ff)
        return q_ctx, dss

    @classmethod
    def get_rows(
        cls, queries: List[ReportQuery], ctx: Dict[str, Any], root_band: Optional[BandData] = None
    ) -> Optional[pl.DataFrame]:
        """
        Getting Band rows
        Attrs:
            queries:
            ctx:
            root_band:
        """
        if not queries:
            return None
        rows, joined, joined_field = None, len(queries) > 1, None
        for num, query in enumerate(queries):
            q_ctx, dss = cls.merge_ctx(ctx, query, joined=bool(num))
            data, key_field = None, None
            if query.json_data:
                # return join fields (last DS)
                data = pl.DataFrame(orjson.loads(query.json_data))
            elif num and query.datasource and query.datasource not in dss:
                # Skip not requested DataSource
                logger.warning("[%s] Skipping not registered DataSource", query.datasource)
                continue
            elif query.datasource:
                logger.info("[%s] Query DataSource", query.datasource)
                data, key_field = cls.query_datasource(query, q_ctx, joined_field=joined_field)
                if not joined_field:
                    joined_field = key_field
            if query.query:
                logger.debug("Execute query: %s; Context: %s", query.query, q_ctx)
                sql = pl.SQLContext()
                sql.register(
                    query.datasource or root_band.name,
                    data.lazy() if data is not None else root_band.rows.lazy(),
                )
                data = sql.execute(Jinja2Template(query.query).render(q_ctx), eager=True)
                if query.transpose:
                    data = data.transpose(include_header=True)
            if num and (data is None or data.is_empty()):
                # for join query check data exists
                logger.info("Skipping empty data")
                continue
            elif data is None:
                raise ValueError("First query without result")
            elif data.is_empty():
                # If first query is empty, nothing to join
                return data
            if rows is not None and joined_field:
                # df_left_join = df_customers.join(df_orders, on="customer_id", how="left")
                rows = rows.join(data, on=joined_field, how="left")
            else:
                rows = data
        if joined and joined_field:
            rows = rows.drop(joined_field)
        return rows

    @classmethod
    def query_datasource(
        cls,
        query: ReportQuery,
        ctx: Dict[str, Any],
        joined_field: Optional[str] = None,
    ) -> Tuple[Optional[pl.DataFrame], str]:
        """
        Resolve Datasource for Query
        :param query:
        :param ctx:
        :param joined_field:
        :return:
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
        row = ds.query_sync(**ctx)
        return row, ds.row_index

    def resolve_output_filename(self, run_params: RunParams, root_band: BandData) -> str:
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
