# ----------------------------------------------------------------------
# SimpleReport DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from xlsxwriter.workbook import Workbook

# NOC modules
from .base import DataFormatter
from ..types import OutputType, HEADER_BAND


class SimpleTableFormatter(DataFormatter):
    """
    Simple formatter. Used Band format from config for build docs with section:
        * Text Section
        * Table section
        * Matrix Section
        * Delimiter
    Sections based on Band Config (Direction and format):
        * header band - used for report title and common column description (for root)
        * table section - if BandFormat has Column format
        * matrix section - if Direction set to cross
        * Delimiter set for bands on common level
    """

    MAX_SHEET_NAME = 30

    def render_document(self):
        """
        Format for Root Band data as table
        """
        header_format = self.get_band_format(HEADER_BAND)
        # Column title map
        HEADER_ROW = {}
        sort_index = []
        if header_format:
            for col in header_format.columns:
                *_, col_name = col.name.rsplit(".", 1)
                HEADER_ROW[col_name] = col.title
                sort_index.append(col_name)
        if not self.root_band.has_rows:
            return
        data = self.root_band.get_rows()[0]
        out_columns = sorted(
            [c for c in data.columns if not HEADER_ROW or c in HEADER_ROW],
            key=lambda x: sort_index.index(x) if x in sort_index else 200,
        )
        self.logger.debug("[SIMPLETABLE] Out columns: %s;;;%s", out_columns, HEADER_ROW)
        if self.output_type in {OutputType.CSV, OutputType.SSV, OutputType.CSV_ZIP}:
            r = self.csv_delimiter.join(HEADER_ROW.get(cc, cc) for cc in out_columns) + "\n"
            r += data.select(out_columns).write_csv(
                # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                # columns=out_columns,
                separator=self.csv_delimiter,
                quote_char='"',
                include_header=False,
            )
            self.output_stream.write(r.encode("utf8"))
        elif self.output_type == OutputType.XLSX:
            book = Workbook(self.output_stream, options={"remove_timezone": True})
            worksheet = book.add_worksheet(
                self.report_template.output_name_pattern[: self.MAX_SHEET_NAME]
            )
            data.select(out_columns).write_excel(
                workbook=book,
                worksheet=worksheet.name,
                autofit=True,
                position="A1",
            )
            cf1 = book.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            for cn, col in enumerate(out_columns):
                worksheet.write(0, cn, HEADER_ROW.get(col, col), cf1)
            book.close()

    @staticmethod
    def get_col_widths(dataframe, out_columns, index_filed: Optional[str] = None):
        # Then, we concatenate this to the max of the lengths
        # of column name and its values for each column, left to right
        r = [max([len(str(s)) for s in dataframe[col]] + [len(col)]) for col in out_columns]
        # First we find the maximum length of the index column
        if index_filed:
            idx_max = max([len(str(s)) for s in dataframe[index_filed]] + [len(str(index_filed))])
            return [idx_max] + r
        return r
