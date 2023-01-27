# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Dict, Any, Iterable
from io import BytesIO

# Third-party modules
from polars import DataFrame

# NOC modules
from .types import Template, BandOrientation, ReportField, OutputType, RunParams
from .types import Report as ReportParam
# from .formatter.loader import loader as f_loader
from ..datasources.loader import loader as ds_loader

logger = logging.getLogger(__name__)


class BandData(object):
    """
    Report Data for Band
    """
    ROOT_BAND_NAME = "Root"

    def __init__(
            self,
            name: str,
            parent_band: Optional["BandData"] = None,
            orientation: BandOrientation = BandOrientation.HORIZONTAL
    ):
        self.name = name
        self.parent = parent_band
        self.orientation = orientation
        self.data: Dict[str, Any] = {}
        self.children_bands: Dict[str, "BandData"] = {}
        self.report_field_format: Dict[str, ReportField] = {}

    def iter_children_bands(self) -> Iterable["BandData"]:
        """
        Itarate over children bands
        :return:
        """
        for b in self.children_bands:
            yield b

    @property
    def full_name(self):
        if not self.parent:
            return self.name
        return f"{self.parent.name}.{self.name}"

    def add_child(self, band: "BandData"):
        if band.name not in self.children_bands:
            self.children_bands[band.name] = band

    def set_data(self, data: Dict[str, Any]):
        self.data.update(data.copy())


class Report(object):
    """
    Reporting Engine implementation
    """

    def __init__(
            self,
            report: Report,
            document_name: str,
            output_type: str,
            content: Optional[bytes] = None
    ):
        """

        :param report: Report Instance
        :param document_name: Output file name for content
        :param output_type: Output document type
        :param content: Output content
        """
        self.report = report
        self.document_name = document_name
        self.content = content or BytesIO()
        self.output_type = output_type
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
        params = r_params.params
        out_type = r_params.output_type
        self.logger.info("[%s] Running report with parameter: %s", self.report, params)
        cleaned_param = self.clean_param(params)
        data = self.load_data(cleaned_param)
        self.generate_report(template, out_type, out, cleaned_param, data)
        self.logger.info("[%s] Finished report with parameter: %s", self.report, cleaned_param)
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

    def clean_param(self, params: Dict[str, Any]):
        """
        Clean and validata input params
        :param params:
        :return:
        """
        clean_params = params.copy()
        for p in self.report.parameters:
            name = p.alias
            value = params.get(name)
            if value is None and p.required:
                raise ValueError(f"Required parameter {name} not found")
        return clean_params

    def load_data(self, params: Dict[str, Any]) -> BandData:
        """
        Load report data from band
        :return:
        """
        r = BandData(BandData.ROOT_BAND_NAME)
        r.set_data(params)
        return r

    def resolve_output_filename(self) -> str:
        """
        Return document filename by
        :return:
        """
