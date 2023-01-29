# ----------------------------------------------------------------------
# DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from io import BytesIO

# NOC modules
from ..types import ReportBand, Template, OutputType


class DataFormatter(object):
    """
    Base class for Report Formatter
    Create result document by setted format
    """

    def __init__(self, root_band: ReportBand, template: Template, output_type: OutputType):
        self.root_band = root_band
        self.report_template = template
        self.output_type = output_type
        self.output_stream = b""

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
