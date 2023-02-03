# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Dict, Any, Optional, List, Iterable

# Third-party modules
import orjson
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
from .types import Template, OutputType, RunParams, Report, ReportQuery, ReportBand
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
        from noc.core.reporter.formatter.loader import loader as df_loader

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

    def iter_bands_data(
        self, report_band: ReportBand, root_band: BandData, root
    ) -> Iterable[BandData]:
        """

        :param rb:
        :param root_band:
        :return:
        """
        rows: Optional[pl.DataFrame] = self.get_rows(
            report_band.queries, root_band.get_data(), root_band=root
        )
        if not report_band.children:
            band = BandData(report_band.name, root_band, report_band.orientation)
            band.rows = rows
            yield band
            return
        for d in rows.sort("mac").to_dicts():
            band = BandData(report_band.name, root_band, report_band.orientation)
            band.set_data(d)
            yield band

    def load_data(self, report: Report, params: Dict[str, Any]) -> BandData:
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
        root.rows = self.get_rows(report_band.queries, params)
        # Extract data from ReportBand
        for rb in report_band.iter_nester():
            bd_parent = root.find_band_recursively(rb.parent.name)
            logger.info(
                "Proccessed ReporBand: %s; Parent BandData: %s", rb.name, bd_parent
            )  # Level needed ?
            if bd_parent.parent:
                # Fill parent DataBand children row
                for c in bd_parent.parent.get_children_by_name(rb.parent.name):
                    for band in self.iter_bands_data(rb, c, root):
                        bd_parent.add_child(band)
                continue
            for band in self.iter_bands_data(rb, bd_parent, root):
                bd_parent.add_child(band)
        return root

    def get_rows(
        self, queries: List[ReportQuery], ctx: Dict[str, Any], root_band: Optional[BandData] = None
    ) -> Optional[pl.DataFrame]:
        """

        :param queries:
        :param ctx:
        :param root_band:
        :return:
        """
        if not queries:
            return None
        rows = None
        for query in queries:
            data = None
            if query.json:
                data = pl.DataFrame(orjson.loads(query.json))
            if query.datasource:
                data = self.query_datasource(query, ctx)
            if query.query:
                logger.debug("Execute query: %s; Context: %s", query.query, ctx)
                data = eval(
                    query.query,
                    {"__builtins__": {}},
                    {"ds": data, "ctx": ctx, "root_band": root_band, "pl": pl},
                )
            if data is None or data.is_empty():
                continue
            if rows is not None:
                # @todo Linked field!
                rows = rows.join(data)
                continue
            rows = data
        return rows

    def query_datasource(self, query: ReportQuery, ctx: Dict[str, Any]) -> Optional[pl.DataFrame]:
        """

        :param query:
        :param ctx:
        :return:
        """
        from noc.core.datasources.loader import loader as ds_loader

        ds = ds_loader[query.datasource]
        if not ds:
            raise ValueError(f"Unknown Datasource: {query.datasource}")
        params = query.params or {}
        params.update(ctx)
        if query.fields:
            params["fields"] = query.fields
        row = ds.query_sync(**params)
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
