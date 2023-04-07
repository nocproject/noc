# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
import datetime

# Python modules
import logging
from io import BytesIO
from typing import Dict, Any, Optional, List, Iterable, Tuple, Set

# Third-party modules
import orjson
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
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
from noc.main.reportsources.loader import loader as r_source_loader


logger = logging.getLogger(__name__)


class ReportEngine(object):
    """
    Reporting Engine implementation. Report Pipeline:
    RunParams -> ReportEngine -> load_data -> DataBand -> Formatter -> DocumentFile
    """

    def __init__(self):
        self.logger = logger

    def run_report(self, r_params: RunParams):
        """
        Run report withs params
        :param r_params: Report params
        :param out: Output document
        :return:
        """
        # Handler param
        out: BytesIO = BytesIO()
        report = r_params.report
        template = r_params.get_template()
        out_type = r_params.output_type or template.output_type
        cleaned_param = self.clean_param(report, r_params.get_params())
        start = datetime.datetime.now()
        self.logger.info("[%s] Running report with parameter: %s", report, cleaned_param)
        try:
            data = self.load_data(report, cleaned_param)
        except Exception as e:
            self.register_execute(
                report, start, cleaned_param, error_text=f"Error when load Data: {str(e)}"
            )
            return
        try:
            self.generate_report(report, template, out_type, out, cleaned_param, data)
        except Exception as e:
            self.register_execute(
                report, start, cleaned_param, error_text=f"Error when format result: {str(e)}"
            )
            return
        self.logger.info("[%s] Finished report with parameter: %s", report, cleaned_param)
        self.register_execute(report, start, cleaned_param, successfully=True)
        output_name = self.resolve_output_filename(run_params=r_params, root_band=data)
        return OutputDocument(
            content=out.getvalue(), document_name=output_name, output_type=out_type
        )

    def register_execute(
        self,
        report: ReportConfig,
        start: datetime.datetime,
        params: Dict[str, Any],
        end: Optional[datetime.datetime] = None,
        successfully: bool = False,
        canceled: bool = False,
        error_text: Optional[str] = None,
    ):
        """
        :param report:
        :param start:
        :param end:
        :param params:
        :param successfully:
        :param canceled:
        :param error_text:
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
                    "end": end.replace(0).isoformat(),
                    "duration": (start - end).total_seconds(),
                    "report": report.name,
                    "name": report.name,
                    "code": "",
                    "user": "",
                    "successfully": successfully,
                    "canceled": canceled,
                    "params": params,
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
        """
        Render document
        :return:
        """
        #
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

    def iter_bands_data(
        self, report_band: ReportBand, root_band: BandData, root
    ) -> Iterable[BandData]:
        """

        :param report_band:
        :param root_band:
        :return:
        """
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
        :param report:
        :param params:
        :return:
        """
        report_band = report.get_root_band()
        # Create Root BandData
        root = BandData(BandData.ROOT_BAND_NAME)
        root.set_data(params)
        if report_band.source:
            s = r_source_loader[report_band.source]()
            root.format = s.get_format()
            root.add_children(s.get_data(**params))
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
                    for band in self.iter_bands_data(rb, c, root):
                        c.add_child(band)
                continue
            for band in self.iter_bands_data(rb, bd_parent, root):
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
        :param ctx:
        :param query:
        :param joined:
        :return:
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
        :param queries:
        :param ctx:
        :param root_band:
        :return:

        """
        if not queries:
            return None
        rows = None
        # key_field = "managed_object_id"
        for num, query in enumerate(queries):
            q_ctx, dss = cls.merge_ctx(ctx, query, joined=bool(num))
            data, key_field = None, None
            if query.json_data:
                # return join fields (last DS)
                data = pl.DataFrame(orjson.loads(query.json_data))
            elif num and query.datasource and dss and query.datasource not in dss:
                continue
            elif query.datasource:
                logger.info("[%s] Query datasource", query.datasource)
                data, key_field = cls.query_datasource(query, q_ctx, joined=len(queries) > 1)
            if query.query:
                logger.debug("Execute query: %s; Context: %s", query.query, q_ctx)
                data = eval(
                    query.query,
                    {"__builtins__": {}},
                    {"ds": data, "ctx": q_ctx, "root_band": root_band, "pl": pl},
                )
            if data is None or data.is_empty():
                continue
            if rows is not None and key_field:
                # @todo Linked field!
                # df_left_join = df_customers.join(df_orders, on="customer_id", how="left")
                rows = rows.join(data, on=key_field, how="left")
                continue
            else:
                rows = data
        if key_field and len(queries) > 1:
            rows = rows.drop(key_field)
        return rows

    @classmethod
    def query_datasource(
        cls, query: ReportQuery, ctx: Dict[str, Any], joined: bool = False
    ) -> Tuple[Optional[pl.DataFrame], str]:
        """
        Resolve Datasource for Query
        :param query:
        :param ctx:
        :param joined:
        :return:
        """
        from noc.core.datasources.loader import loader as ds_loader

        ds = ds_loader[query.datasource]
        if not ds:
            raise ValueError(f"Unknown Datasource: {query.datasource}")
        if joined and ctx.get("fields"):
            ctx["fields"] += [ds.row_index]
            # Check not row_index
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
        return f"{Jinja2Template(output_name).render(ctx) or 'report'}.{out_type.value}"
