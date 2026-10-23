# ----------------------------------------------------------------------
# DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from io import BytesIO

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.core.reporter.band import Band
from noc.core.reporter.types import Template, OutputType, BandFormat
from noc.config import config

logger = logging.getLogger(__name__)


class DataFormatter:
    """
    Base class for Report Formatter
    Create result document by setted format
    """

    label: str | None = None

    def __init__(
        self,
        root_band: Band,
        template: Template,
        output_type: OutputType,
        output_stream: BytesIO,
        selected_fields: list[str] | None = None,
    ):
        self.root_band = root_band
        self.report_template = template
        self.output_type = output_type
        self.output_stream: BytesIO = output_stream or BytesIO()
        self.selected_fields = selected_fields
        self.csv_delimiter = config.web.report_csv_delimiter
        self.logger = logger

    def __str__(self) -> str:
        return f"DataFormatter/{self.__class__.__name__}"

    def __repr__(self) -> str:
        return (
            f"DataFormatter/{self.__class__.__name__} ("
            f"root_band: {self.root_band}, "
            f"report_template: {self.report_template}, "
            f"output_type: {self.output_type})"
        )

    def get_band_format(self, band: str) -> BandFormat | None:
        if self.report_template.bands_format and band in self.report_template.bands_format:
            return self.report_template.bands_format[band]

    def render_document(self):
        """
        Render document content. Override on child class
        :return:
        """

    def create_document(self) -> bytes:
        """
        Create document method
        :return:
        """
        self.output_stream = BytesIO()
        self.render_document()
        return self.output_stream


data_formatter_loader = Loader[type[DataFormatter]](
    bases=config.iter_customized_bases("noc.core.reporter.formatter"),
    exclude=("base",),
)
