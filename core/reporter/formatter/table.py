# ----------------------------------------------------------------------
# CSV DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import csv

# NOC modules
from .base import DataFormatter
from ..types import OutputType


class TableFormatter(DataFormatter):
    def render_document(self):
        """

        :return:
        """
        if self.report_template.output_type == OutputType.CSV:
            self.render_csv(separator=",")
        elif self.report_template.output_type == OutputType.SSV:
            self.render_csv()

    def render_csv(self, separator: str = ";"):
        csv_header = None
        columns_map = self.report_template.columns_format or {}
        header_map = {}
        for c_name, c_format in columns_map.items():
            header_map[c_name] = c_format.title or c_name
        for rb in self.root_band.iter_all_bands():
            if rb.rows is None or rb.rows.is_empty():
                continue
            if not rb.children_bands:
                if not csv_header:
                    csv_header = (
                        separator.join(header_map.get(cc, cc) for cc in rb.rows.columns) + "\n"
                    )
                    self.output_stream.write(csv_header.encode("utf8"))
                if rb.parent and not rb.parent.is_root:  # Section
                    self.output_stream.write(f"{rb.parent.title}\n".encode("utf8"))
                rb.rows.write_csv(
                    # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                    file=self.output_stream,
                    sep=separator,
                    quote='"',
                    has_header=False,
                )
