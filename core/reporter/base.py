# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Dict, Any

# NOC modules
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
        :return:
        """
        r = BandData(BandData.ROOT_BAND_NAME)
        r.set_data(params)
        r.datasource = report.root_band.query
        return r

    def resolve_output_filename(self) -> str:
        """
        Return document filename by
        :return:
        """
