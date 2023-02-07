# ----------------------------------------------------------------------
# CSV DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import DataFormatter


class TableFormatter(DataFormatter):
    def render_document(self):
        """

        :return:
        """
        csv_header = None
        for rb in self.root_band.iter_all_bands():
            if rb.rows is None or rb.rows.is_empty():
                continue
            if not rb.children_bands:
                if not csv_header:
                    csv_header = ";".join(cc for cc in rb.rows.columns) + "\n"
                    self.output_stream.write(csv_header.encode("utf8"))
                if rb.parent and not rb.parent.is_root:  # Section
                    self.output_stream.write(f"{rb.parent.title}\n".encode("utf8"))
                rb.rows.write_csv(
                    # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                    file=self.output_stream,
                    sep=";",
                    quote='"',
                    has_header=False,
                )
