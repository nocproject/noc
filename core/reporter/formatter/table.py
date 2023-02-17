# ----------------------------------------------------------------------
# CSV DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import csv
import os
from typing import Dict
from io import StringIO

# NOC modules
from .base import DataFormatter
from ..types import OutputType


class TableFormatter(DataFormatter):
    def render_document(self):
        """

        :return:
        """
        if self.report_template.output_type == OutputType.CSV:
            self.render_csv(delimiter=",")
        elif self.report_template.output_type == OutputType.SSV:
            self.render_csv()

    def get_fields(self, rows=None) -> Dict[str, str]:
        """
        Return field_name -> field header map
        :param rows:
        :return:
        """
        r = {}
        if not self.report_template.columns_format:
            return {fn: fn for fn in rows.columns}
        for c_name, c_format in self.report_template.columns_format.items():
            r[c_name] = c_format.title or c_name
        return r

    def render_csv(self, delimiter: str = ";"):
        fields = None
        for rb in self.root_band.iter_all_bands():
            if rb.rows is None or rb.rows.is_empty():
                continue
            if not rb.children_bands:
                if not fields:
                    fields = self.get_fields(rb.rows)
                    csv_header = delimiter.join(fields[ll] for ll in fields) + os.linesep
                    self.output_stream.write(csv_header.encode("utf8"))
                if rb.parent and not rb.parent.is_root:  # Section
                    self.output_stream.write(f"{rb.parent.title}{os.linesep}".encode("utf8"))
                rb.rows.write_csv(
                    # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                    file=self.output_stream,
                    sep=delimiter,
                    quote='"',
                    has_header=False,
                )
