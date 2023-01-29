# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Dict, Any

# Third-party modules
import orjson

# NOC modules
from noc.core.datasources.loader import loader as ds_loader
from noc.core.reporter.formatter.loader import df_loader
from .types import Template, OutputType, RunParams, Report
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
        template = r_params.report_template
        out_type = r_params.output_type or template.output_type
        cleaned_param = self.clean_param(report, r_params.params)
        self.logger.info("[%s] Running report with parameter: %s", report, cleaned_param)
        data = self.load_data(report, cleaned_param)
        self.generate_report(template, out_type, out, cleaned_param, data)
        self.logger.info("[%s] Finished report with parameter: %s", report, cleaned_param)
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
        formatter(band_data, template, output_type, output_stream)
        formatter.renderDocument()

    def clean_param(self, report: Report, params: Dict[str, Any]):
        """
        Clean and validata input params
        :param report:
        :param params:
        :return:
        """
        clean_params = params.copy()
        for p in report.parameters:
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
        r = BandData(BandData.ROOT_BAND_NAME)
        r.set_data(params)
        # Extract data
        rb = report.get_root_band()
        for cb in rb.iter_children():
            bd = BandData(cb.name, r, cb.orientation)
            for c in cb.queries:
                if c.datasource:
                    data = ds_loader[c.datasource]
                    bd.rows = data.run_sync(**r.data)
                    # Parse Query
                if c.json:
                    bd.rows = orjson.loads(c.data)
            if bd.rows:
                bd.set_data(bd.rows[0])
            r.add_child(bd)
        return r

    def resolve_output_filename(self) -> str:
        """
        Return document filename by
        :return:
        """
