# ----------------------------------------------------------------------
# DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from io import BytesIO

# NOC modules
from ..types import Template, OutputType, BandFormat
from noc.core.reporter.report import Band
from noc.config import config


class DataFormatter(object):
    """
    Base class for Report Formatter
    Create result document by setted format
    """

    label: Optional[str] = None

    def __init__(
        self,
        root_band: Band,
        template: Template,
        output_type: OutputType,
        output_stream: BytesIO,
    ):
        self.root_band = root_band
        self.report_template = template
        self.output_type = output_type
        self.output_stream: BytesIO = output_stream or BytesIO()
        self.csv_delimiter = config.web.report_csv_delimiter

    def get_band_format(self, band: str) -> Optional[BandFormat]:
        if self.report_template.bands_format and band in self.report_template.bands_format:
            return self.report_template.bands_format[band]

    def render_document(self):
        """
        Render document content. Override on child class
        :return:
        """
        ...

    def create_document(self) -> bytes:
        """
        Create document method
        :return:
        """
        self.output_stream = BytesIO()
        self.render_document()
        return self.output_stream
