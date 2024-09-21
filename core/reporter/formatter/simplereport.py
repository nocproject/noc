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
    def get_columns_format(cls, bf: BandFormat) -> List[TableColumn]:
        """Return Columns by band Format"""
        if not bf.columns:
            return []
        columns = []
        for c in bf.columns:
            if c.format_type or c.total:
                columns.append(
                    TableColumn(
                        c.name,
                        c.title,
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
                        c.title,
                    )
                ]
        return columns

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
        fields = [c.name for c in columns]
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
            for row in rb.iter_data_rows(fields):
                # data.append([row.get(f, "") for f in fields])
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
