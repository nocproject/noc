# ----------------------------------------------------------------------
# SimpleReport DataFormatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional

# Third-party modules
from jinja2 import Template as Jinja2Template
from xlsxwriter.workbook import Workbook

# NOC modules
from .base import DataFormatter
from ..types import OutputType, BandFormat, HEADER_BAND
from ..report import Band
from noc.services.web.base.simplereport import (
    Report,
    TextSection,
    TableSection,
    SectionRow,
    TableColumn,
)


class SimpleReportFormatter(DataFormatter):
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

    def render_document(self):
        """"""
        if self.report_template.output_type != OutputType.HTML:
            self.render_table()
            return
        report = Report()
        for s in self.render_sections():
            report.append_section(s)
        if self.output_type == OutputType.CSV:
            r = report.to_csv(delimiter=self.csv_delimiter)
        elif self.output_type == OutputType.SSV:
            r = report.to_csv(delimiter=";")
        elif self.output_type == OutputType.HTML:
            r = report.to_html(include_buttons=False)
        elif self.output_type == OutputType.XLSX:
            r = report.to_csv(delimiter=";")
            workbook = Workbook(self.output_stream)
            worksheet = workbook.add_worksheet()
            for r, row in enumerate(r.splitlines()):
                for c, col in enumerate(row.split(";")):
                    worksheet.write(r, c, col)
            workbook.close()
            return
        else:
            raise NotImplementedError(f"Output Type {self.output_type} not supported")
        self.output_stream.write(r.encode("utf8"))

    def get_report_title(self) -> str:
        """Getting report title"""
        header = self.get_band_format(HEADER_BAND)
        if header:
            return header.title_template
        return "Report 1"  # Report Title

    @staticmethod
    def get_title(band, template: Optional[str] = None) -> str:
        """Render Band Title if setting template"""
        if not template:
            return band.name
        return Jinja2Template(template).render(band.get_data())

    @classmethod
    def get_columns_format(cls, band: BandFormat) -> List[TableColumn]:
        """Return Columns by band Format"""
        if not band.columns:
            return []
        columns = []
        for c in band.columns:
            if c.format_type or c.total:
                columns.append(
                    TableColumn(
                        c.name,
                        c.title or "",
                        align=c.align.name.lower(),
                        format=c.format_type,
                        total=c.total,
                        total_label=c.total_label,
                    )
                )
            else:
                columns += [
                    TableColumn(
                        c.name,
                        c.title or "",
                    )
                ]
        return columns

    def get_table_section(
        self, band: Band, header_columns: List[TableColumn]
    ) -> Optional[TableSection]:
        """"""
        bf = self.get_band_format(band.name)
        if bf and bf.columns:
            columns = self.get_columns_format(bf)
        elif header_columns:
            columns = header_columns
        else:
            columns = band.get_columns()
        if not columns:
            return
        fields = [getattr(c, "name", c) for c in columns]
        data = []
        if not band.has_rows and band.get_data():
            data.append([band.data.get(f, "") for f in fields])
        for row in band.iter_rows():
            data.append([row.get(f, "") for f in fields])
        return data

    def get_report_columns(self) -> List[TableColumn]:
        """
        Report Columns used for print report table data
        Column may be set:
        1. On Header Band Format
        2. On Rows datasource
        3. Exception
        """
        header_format = self.get_band_format(HEADER_BAND)
        columns = []
        if header_format:
            columns = self.get_columns_format(header_format)
        if not columns and self.root_band.has_rows:
            columns = [TableColumn(name=c, title=c) for c in self.root_band.get_columns()]
        if columns:
            return columns
        # Getting last data band
        for rb in self.root_band.iter_nested_bands():
            if rb.has_children:
                continue
            bf = self.get_band_format(rb.name)
            if bf and bf.columns:
                columns = self.get_columns_format(bf)
                if columns:
                    return columns
            if rb.has_rows:
                return [TableColumn(name=c, title=c) for c in rb.get_columns()]

    def render_sections(self):
        columns = self.get_report_columns()
        if not columns:
            raise ValueError("Not setting column for Report")
        data = []
        for rb in self.root_band.iter_report_bands():
            if rb.name == HEADER_BAND:
                # Skip Header Band
                continue
            bf = self.get_band_format(rb.name)
            # Section Row
            if not rb.is_root and bf and bf.title_template:
                data.append(SectionRow(self.get_title(rb, bf.title_template)))
            if rb.has_children:
                continue
            fields = [getattr(c, "name", c) for c in columns]
            for row in rb.iter_rows(fields):
                data.append(row)
            # Table Section
            # tb = self.get_table_section(rb, header_columns)
            # if not tb:
            #    continue
            # data.append(tb)
            # If not Header Columns, set it from last Band
        return [
            TextSection(title=self.get_report_title()),
            TableSection(columns=columns, data=data, enumerate=False),
        ]

    def render_table(self):
        """
        Format for Root Band data as table
        :return:
        """
        band = self.root_band.children_bands[0]
        r_format = self.report_template.bands_format[band.name]
        # Column title map
        HEADER_ROW = {}
        for col in r_format.columns:
            *_, col_name = col.name.rsplit(".", 1)
            HEADER_ROW[col_name] = col.title
        if not self.root_band.has_rows:
            return
        data = self.root_band.get_rows()[0]
        out_columns = [c for c in data.columns]
        if self.output_type in {OutputType.CSV, OutputType.SSV, OutputType.CSV_ZIP}:
            r = self.csv_delimiter.join(HEADER_ROW.get(cc, cc) for cc in data.columns) + "\n"
            r += data.select(out_columns).write_csv(
                # header=[self.HEADER_ROW.get(cc, cc) for cc in out_columns],
                # columns=out_columns,
                separator=self.csv_delimiter,
                quote_char='"',
                include_header=False,
            )
            self.output_stream.write(r.encode("utf8"))
        elif self.output_type == OutputType.XLSX:
            book = Workbook(self.output_stream)
            cf1 = book.add_format({"bottom": 1, "left": 1, "right": 1, "top": 1})
            worksheet = book.add_worksheet(self.report_template.output_name_pattern)
            for cn, col in enumerate(out_columns):
                worksheet.write(0, cn, HEADER_ROW.get(col, col), cf1)
            for cn, col in enumerate(out_columns):
                worksheet.write_column(1, cn, data[col], cf1)
            (max_row, max_col) = data.shape
            worksheet.autofilter(0, 0, max_row, len(out_columns))
            worksheet.freeze_panes(1, 0)
            for i, width in enumerate(self.get_col_widths(data)):
                worksheet.set_column(i, i, width)
            #
            book.close()

    @staticmethod
    def get_col_widths(dataframe, index_filed: Optional[str] = None):
        # Then, we concatenate this to the max of the lengths
        # of column name and its values for each column, left to right
        r = [max([len(str(s)) for s in dataframe[col]] + [len(col)]) for col in dataframe.columns]
        # First we find the maximum length of the index column
        if index_filed:
            idx_max = max([len(str(s)) for s in dataframe[index_filed]] + [len(str(index_filed))])
            return [idx_max] + r
        return r
