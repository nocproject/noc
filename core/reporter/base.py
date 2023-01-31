# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Dict, Any, Optional

# Third-party modules
import orjson
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
from noc.core.datasources.loader import loader as ds_loader
from noc.core.reporter.formatter.loader import loader as df_loader
from .types import Template, OutputType, RunParams, Report, ReportQuery
from .report import BandData


logger = logging.getLogger(__name__)


class ReportEngine(object):
    """
    Reporting Engine implementation
    """

    def __init__(self):
        self.logger = logger

    def run_report(self, r_params: RunParams, out: bytes):
        """
        Run report
        :param r_params: Report params
        :param out:
        :return:
        """
        # Handler param
        report = r_params.report
        template = r_params.get_template()
        out_type = r_params.output_type or template.output_type
        cleaned_param = self.clean_param(report, r_params.get_params())
        self.logger.info("[%s] Running report with parameter: %s", report, cleaned_param)
        data = self.load_data(report, cleaned_param)
        self.generate_report(report, template, out_type, out, cleaned_param, data)
        self.logger.info("[%s] Finished report with parameter: %s", report, cleaned_param)
        output_name = self.resolve_output_filename(run_params=r_params, root_band=data)
        return out

    def generate_report(
        self,
        report: Report,
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
        formatter = df_loader[output_type.value]
        fmt = formatter(band_data, template, output_type, output_stream)
        fmt.render_document()

    def clean_param(self, report: Report, params: Dict[str, Any]):
        """
        Clean and validata input params
        :param report:
        :param params:
        :return:
        """
        clean_params = params.copy()
        for p in report.parameters or []:
            name = p.alias
            value = params.get(name)
            if value is None and p.required:
                raise ValueError(f"Required parameter {name} not found")
        return clean_params

    def load_data(self, report: Report, params: Dict[str, Any]) -> BandData:
        """
        Load report data from band
        1. Create root DataBand
        2. Extract data from report band
        3. Merge root DataBand and Extract Data
            1. If not queries - from params
            2. If queries - get parent band params and execute query
        :return:
        """
        root = BandData(BandData.ROOT_BAND_NAME)
        root.set_data(params)
        ctxs = {}
        # Extract data
        report_band = report.get_root_band()
        for q in report_band.queries:
            root.rows = self.get_rows(q, root.get_data())
        for rb in report_band.iter_nester():
            if rb.parent.name == BandData.ROOT_BAND_NAME:
                bd_root = root
            else:
                bd_root = ctxs[rb.parent.name]
            bd = BandData(rb.name, bd_root, rb.orientation)
            bd.set_data(bd_root.get_data())
            ctxs[bd.name] = bd
            for q in rb.queries:
                data = self.get_rows(q, bd.get_data(), p_rows=bd_root.rows)
                if data is None:
                    continue
                bd.rows = data
                bd.set_data(dict(zip(data.columns, data.row(0))))
            root.add_child(bd)
        return root

    def get_rows(
        self, query: "ReportQuery", ctx: Dict[str, Any], p_rows: Optional[pl.DataFrame] = None
    ) -> Optional[pl.DataFrame]:
        """

        :param query:
        :param ctx:
        :return:
        """
        if query.json:
            return pl.DataFrame(orjson.loads(query.json))
        if not query.datasource and not query.query:
            return None
        row = None
        if query.datasource:
            ds = ds_loader[query.datasource]
            if not ds:
                raise ValueError(f"Unknown Datasource: {query.datasource}")
            params = query.params or {}
            params.update(ctx)
            if query.fields:
                params["fields"] = query.fields
            row = ds.query_sync(**params)
        logger.info("Execute query: %s; Context: %s", query.query, ctx)
        if query.query:
            row = eval(
                query.query,
                {"__builtins__": {}},
                {"ds": row, "ctx": ctx, "parent": p_rows, "pl": pl},
            )
        return row

    def resolve_output_filename(self, run_params: RunParams, root_band: BandData) -> str:
        """
        Return document filename by
        :return:
        """
        template = run_params.get_template()
        output_name = template.get_document_name()
        ctx = root_band.get_data()
        return Jinja2Template(output_name).render(ctx)
